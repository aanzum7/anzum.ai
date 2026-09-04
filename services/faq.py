# ──────────────────────────────────────────────────────────────────────────────
# file: services/faq.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from difflib import SequenceMatcher
import re
from typing import Dict, List, Optional, Set, Tuple

STOPWORDS: Set[str] = {
    "a", "about", "an", "and", "are", "as", "at", "be", "by", "can", "could",
    "do", "does", "for", "from", "how", "i", "in", "is", "it", "me", "my",
    "of", "on", "or", "tell", "the", "to", "was", "what", "when", "where",
    "which", "who", "why", "with", "would", "you", "your"
}

def _tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words."""
    return re.findall(r"\b\w+\b", text.lower())

def _meaningful_tokens(text: str) -> Set[str]:
    """Extract significant words excluding common stopwords."""
    tokens = _tokenize(text)
    filtered = {w for w in tokens if w not in STOPWORDS}
    return filtered if filtered else set(tokens)

class FAQHandler:
    """Intelligent FAQ matcher using hybrid sequence and token semantic heuristics."""

    def __init__(self, faq_list: List[Dict]):
        self.faq_list = faq_list

    def find_match_details(
        self, user_input: str, threshold: float = 0.55
    ) -> Optional[Dict[str, str]]:
        """
        Find the most relevant FAQ entry using a combination of:
        - SequenceMatcher ratio
        - Token intersection (Jaccard similarity)
        - Substring inclusion
        """
        if not user_input or not self.faq_list:
            return None

        target = user_input.strip().lower()
        target_tokens = _meaningful_tokens(target)

        best_faq: Optional[Dict] = None
        highest_score = 0.0

        for faq in self.faq_list:
            q_raw = str(faq.get("question", ""))
            q_lower = q_raw.lower()
            q_tokens = _meaningful_tokens(q_lower)
            cat = str(faq.get("category", "")).lower()

            # 1. Sequence ratio
            seq_sim = SequenceMatcher(None, target, q_lower).ratio()

            # 2. Token Jaccard similarity
            token_sim = 0.0
            if target_tokens and q_tokens:
                intersection = target_tokens.intersection(q_tokens)
                union = target_tokens.union(q_tokens)
                token_sim = len(intersection) / len(union) if union else 0.0

                # Check if category matches directly (e.g. "education", "projects")
                if cat and cat in target_tokens:
                    token_sim = max(token_sim, 0.70)

            # 3. Substring containment bonus
            sub_boost = 0.0
            if len(target) >= 4 and target in q_lower:
                sub_boost = 0.82
            elif len(q_lower) >= 4 and q_lower in target:
                sub_boost = 0.88

            # Combined weighted score
            score = max(seq_sim, token_sim, sub_boost)

            if score > highest_score:
                highest_score = score
                best_faq = faq

        if highest_score >= threshold and best_faq:
            return {
                "question": best_faq.get("question", ""),
                "answer": best_faq.get("answer", ""),
                "category": best_faq.get("category", "General"),
                "score": f"{highest_score:.2f}",
            }

        return None

    def find_similar_question(
        self, user_input: str, threshold: float = 0.55
    ) -> Tuple[Optional[str], Optional[str]]:
        """Backwards compatible tuple return (question, answer)."""
        match = self.find_match_details(user_input, threshold=threshold)
        if match:
            return match["question"], match["answer"]
        return None, None
