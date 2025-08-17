# ──────────────────────────────────────────────────────────────────────────────
# file: ui/faq_view.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Dict, List
import streamlit as st

DESIRED_ORDER = [
    "Experience", "Education", "Research", "Work", "Technologies",
    "Skills", "Projects", "Certificates", "Consulting"
]

def render_faq_tabs(faq_data: List[Dict]):
    if not faq_data:
        st.info("No FAQs found.")
        return

    existing_categories = sorted({faq.get("category", "General") for faq in faq_data})
    categories = [c for c in DESIRED_ORDER if c in existing_categories] + [
        c for c in existing_categories if c not in DESIRED_ORDER
    ]

    tabs = st.tabs(categories)

    for i, category in enumerate(categories):
        with tabs[i]:
            category_faqs = [x for x in faq_data if x.get("category") == category]
            if not category_faqs:
                st.caption("_No questions in this category yet._")
            for faq in category_faqs:
                q = faq.get("question", "Untitled")
                a = faq.get("answer", "")
                with st.expander(f"❓ {q}"):
                    st.markdown(a)

