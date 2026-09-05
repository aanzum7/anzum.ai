# ──────────────────────────────────────────────────────────────────────────────
# file: services/cache_manager.py
# ──────────────────────────────────────────────────────────────────────────────
"""
Semantic & normalized response caching for anzum.ai to eliminate redundant
Gemini API calls and prevent quota burn on similar or identical queries.
"""
from __future__ import annotations

from collections import OrderedDict
from difflib import SequenceMatcher
import re
import threading
import time
from typing import Dict, Generator, List, Optional, Set, Tuple

from config.settings import (
    CACHE_SIMILARITY_THRESHOLD,
    CACHE_MAX_ENTRIES,
)

STOPWORDS: Set[str] = {
    "a", "about", "an", "and", "are", "as", "at", "be", "by", "can", "could",
    "do", "does", "for", "from", "how", "i", "in", "is", "it", "me", "my",
    "of", "on", "or", "please", "tell", "the", "to", "was", "what", "when",
    "where", "which", "who", "why", "with", "would", "you", "your"
}

def normalize_text(text: str) -> str:
    """Lowercase, strip non-alphanumeric chars, collapse spaces."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()

def _stem(word: str) -> str:
    """Lightweight suffix stripping for plural and verb forms."""
    w = word.lower()
    for suffix in ("ing", "tion", "tions", "ies", "es", "s", "ed", "ment"):
        if len(w) > len(suffix) + 3 and w.endswith(suffix):
            return w[:-len(suffix)]
    return w

def extract_keywords(text: str) -> Set[str]:
    """Extract non-stopword stemmed tokens."""
    tokens = normalize_text(text).split()
    stems = {_stem(t) for t in tokens if t not in STOPWORDS}
    return stems if stems else {_stem(t) for t in tokens}

class SemanticResponseCache:
    """
    Thread-safe semantic response cache with LRU eviction, exact-match fast path,
    and fuzzy token-similarity matching for rephrased questions.
    """

    def __init__(
        self,
        max_size: int = CACHE_MAX_ENTRIES,
        similarity_threshold: float = CACHE_SIMILARITY_THRESHOLD,
    ):
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        self._lock = threading.Lock()
        # normalized_query -> response_text (OrderedDict for LRU)
        self._cache: OrderedDict[str, str] = OrderedDict()
        # normalized_query -> set of keywords
        self._keywords_index: Dict[str, Set[str]] = {}

    def get(self, query: str) -> Optional[Tuple[str, float]]:
        """
        Check cache for exact or semantically similar query.
        Returns (cached_response, similarity_score) if found, else None.
        """
        norm_query = normalize_text(query)
        if not norm_query:
            return None

        with self._lock:
            # 1. Exact normalized match (Fast path O(1))
            if norm_query in self._cache:
                self._cache.move_to_end(norm_query)
                return self._cache[norm_query], 1.0

            # 2. Semantic & fuzzy similarity match
            query_kws = extract_keywords(norm_query)
            if not query_kws:
                return None

            best_match: Optional[str] = None
            best_score = 0.0

            for cached_norm, response_text in self._cache.items():
                cached_kws = self._keywords_index.get(cached_norm, set())
                if not cached_kws:
                    continue

                # Token Jaccard similarity on stemmed keywords
                intersection = query_kws.intersection(cached_kws)
                union = query_kws.union(cached_kws)
                jaccard = len(intersection) / len(union) if union else 0.0

                # Overlap ratio relative to smaller set
                min_kws = min(len(query_kws), len(cached_kws))
                overlap_ratio = len(intersection) / min_kws if min_kws > 0 else 0.0

                # Token sequence similarity on sorted stemmed keywords
                q_token_str = " ".join(sorted(query_kws))
                c_token_str = " ".join(sorted(cached_kws))
                token_seq = SequenceMatcher(None, q_token_str, c_token_str).ratio()

                # Full normalized text sequence similarity
                full_seq = SequenceMatcher(None, norm_query, cached_norm).ratio()

                # Substring containment bonus
                sub_score = 0.0
                if len(norm_query) >= 10 and norm_query in cached_norm:
                    sub_score = 0.85
                elif len(cached_norm) >= 10 and cached_norm in norm_query:
                    sub_score = 0.85

                combined_score = max(
                    jaccard,
                    (overlap_ratio * 0.70 + token_seq * 0.30) if len(intersection) > 0 else 0.0,
                    full_seq * 0.90 if len(intersection) > 0 else 0.0,
                    sub_score,
                )

                if combined_score > best_score:
                    best_score = combined_score
                    best_match = response_text

            if best_score >= self.similarity_threshold and best_match:
                return best_match, best_score

            return None

    def set(self, query: str, response: str) -> None:
        """Store query and response in cache."""
        norm_query = normalize_text(query)
        if not norm_query or not response:
            return

        with self._lock:
            if norm_query in self._cache:
                self._cache.move_to_end(norm_query)
                self._cache[norm_query] = response
            else:
                if len(self._cache) >= self.max_size:
                    oldest, _ = self._cache.popitem(last=False)
                    self._keywords_index.pop(oldest, None)

                self._cache[norm_query] = response
                self._keywords_index[norm_query] = extract_keywords(norm_query)

    def preseed(
        self,
        faq_data: Optional[List[Dict]] = None,
        suggestion_chips: Optional[List[Tuple[str, str]]] = None,
        personal_context: Optional[Dict] = None,
    ) -> int:
        """Pre-warm the cache with verified FAQs, suggestion chips, and profile facts."""
        count = 0
        faq_data = faq_data or []
        suggestion_chips = suggestion_chips or []

        # 1. Index FAQs
        for faq in faq_data:
            q = faq.get("question", "")
            a = faq.get("answer", "")
            if q and a:
                self.set(q, a)
                count += 1

        # 2. Index Suggestion Chips & common variations
        for label, prompt in suggestion_chips:
            # Match with corresponding FAQ answer if available
            matched_answer = None
            for faq in faq_data:
                if normalize_text(faq.get("question", "")) in normalize_text(prompt) or \
                   normalize_text(prompt) in normalize_text(faq.get("question", "")):
                    matched_answer = faq.get("answer", "")
                    break

            if matched_answer:
                self.set(prompt, matched_answer)
                self.set(label, matched_answer)
                count += 1

        # 3. Index key personal context queries
        if personal_context:
            basic = personal_context.get("basic_info", {})
            name = basic.get("name", "Tanvir Anzum")
            email = basic.get("email", "")
            phone = basic.get("phone", "")
            location = basic.get("location", "Hamburg, Germany")
            status = basic.get("current_status", "")

            if email or phone:
                contact_ans = (
                    f"You can reach Tanvir directly via email at **{email}** "
                    f"or by phone at **{phone}**. He is currently based in **{location}** "
                    f"and also active on [LinkedIn](https://linkedin.com/in/aanzum7)."
                )
                self.set("How can I contact Tanvir?", contact_ans)
                self.set("What is Tanvir's email and phone?", contact_ans)
                self.set("Where is Tanvir located?", f"Tanvir is based in **{location}** ({status}).")
                count += 3

        return count

    def stream_cached_response(self, text: str) -> Generator[str, None, None]:
        """
        Yield cached text with a micro-delay so the user gets
        the same satisfying typewriter animation without API latency.
        """
        words = text.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == len(words) - 1 else word + " "
            yield chunk
            # Micro-pause for 8 milliseconds between words
            time.sleep(0.008)


# Global singleton cache instance
_GLOBAL_CACHE: Optional[SemanticResponseCache] = None

def get_response_cache() -> SemanticResponseCache:
    global _GLOBAL_CACHE
    if _GLOBAL_CACHE is None:
        _GLOBAL_CACHE = SemanticResponseCache()
    return _GLOBAL_CACHE
