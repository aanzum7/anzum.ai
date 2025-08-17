# ──────────────────────────────────────────────────────────────────────────────
# file: services/faq.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

class FAQHandler:
    """Finds the most similar FAQ entry given a user query."""

    def __init__(self, faq_list: List[Dict]):
        self.faq_list = faq_list

    def find_similar_question(
        self, user_input: str, threshold: float = 0.65
    ) -> Tuple[Optional[str], Optional[str]]:
        most_similar_question: Optional[str] = None
        best_answer: Optional[str] = None
        highest_similarity: float = 0.0

        target = user_input.lower().strip()
        for faq in self.faq_list:
            q = str(faq.get("question", "")).lower()
            sim = SequenceMatcher(None, target, q).ratio()
            if sim > highest_similarity:
                highest_similarity = sim
                most_similar_question = faq.get("question")
                best_answer = faq.get("answer")

        if highest_similarity >= threshold:
            return most_similar_question, best_answer
        return None, None

