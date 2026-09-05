# ──────────────────────────────────────────────────────────────────────────────
# file: ui/faq_view.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Dict, List, Optional
import streamlit as st

def render_faq_multitabs(faq_data: List[Dict], personal_context: Optional[Dict] = None):
    """
    Render clean, informative FAQ cards.
    Provides concise, verified answers for quick reference without AI redirection
    or duplicate contact information (contact is prominent in the sidebar).
    """
    if not faq_data:
        st.info("No FAQs currently available.")
        return

    faq_map = {f.get("category", ""): f for f in faq_data}

    # Clean subtabs for the core FAQ categories (Get in touch removed as requested)
    subtabs = st.tabs([
        "🎓 Role & TUHH",
        "💼 Experience",
        "⚡ Skills & Stack",
        "🔬 Education & Research",
    ])

    # ── 1. Role & TUHH ──
    with subtabs[0]:
        q_obj = faq_map.get("Role", {})
        q = q_obj.get("question", "What is your current background and what opportunities are you seeking?")
        a = q_obj.get(
            "answer",
            "Incoming Master's student at Hamburg University of Technology (TUHH) with 5 years in data analytics & applied ML. Actively seeking a Werkstudent opportunity in Data Analytics, BI, Data Engineering, or Applied AI in Hamburg."
        )
        st.markdown(
            f"""
            <div class="faq-tab-card">
                <div class="faq-tab-title">
                    <span>🎓</span> {q}
                </div>
                <div class="faq-tab-desc">
                    {a}
                </div>
                <div class="contact-link-row">
                    <span class="contact-link-tag">📍 Hamburg, Germany</span>
                    <span class="contact-link-tag">🎯 M.Sc. Info & Comm Systems @ TUHH</span>
                    <span class="contact-link-tag">🔍 Seeking Werkstudent</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── 2. Experience ──
    with subtabs[1]:
        q_obj = faq_map.get("Experience", {})
        q = q_obj.get("question", "What did you achieve at Prothom Alo and Brain Station 23?")
        a = q_obj.get(
            "answer",
            "At Prothom Alo (Google News Initiative), built collaborative filtering & Word2Vec recommender (cutting memory ~50%, runtime 90 to 10 mins) and Gemini AI tag generator. At Brain Station 23, built Streamlit EDA & ML readiness dashboards."
        )
        st.markdown(
            f"""
            <div class="faq-tab-card">
                <div class="faq-tab-title">
                    <span>💼</span> {q}
                </div>
                <div class="faq-tab-desc">
                    {a}
                </div>
                <div class="contact-link-row">
                    <span class="contact-link-tag">🚀 20M+ Readers Impact</span>
                    <span class="contact-link-tag">⚡ 90m ➔ 10m Runtime</span>
                    <span class="contact-link-tag">🤖 Word2Vec & Collaborative Filtering</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── 3. Skills & Stack ──
    with subtabs[2]:
        q_obj = faq_map.get("Expertise", {})
        q = q_obj.get("question", "What are your core technical skills and tools?")
        a = q_obj.get(
            "answer",
            "Python, SQL (MariaDB, MySQL, BigQuery), recommendation systems (Collaborative Filtering, Word2Vec), Streamlit ML dashboards, Looker Studio, GA4, and Generative AI (Gemini for automated tagging and summarization)."
        )
        st.markdown(
            f"""
            <div class="faq-tab-card">
                <div class="faq-tab-title">
                    <span>⚡</span> {q}
                </div>
                <div class="faq-tab-desc">
                    {a}
                </div>
                <div class="contact-link-row">
                    <span class="contact-link-tag">🐍 Python & SQL</span>
                    <span class="contact-link-tag">📊 Streamlit & Looker</span>
                    <span class="contact-link-tag">🧠 Gemini & RecSys</span>
                    <span class="contact-link-tag">📈 GA4 & BigQuery</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── 4. Education & Research ──
    with subtabs[3]:
        q_obj = faq_map.get("Education", {})
        q = q_obj.get("question", "What is your educational background and research publications?")
        a = q_obj.get(
            "answer",
            "Incoming Master's at TUHH (Hamburg), BSc in CSE from DIU, and ACMP 4.0 from IBA (Dhaka University). Published research on traffic sign recognition and loan fraud prediction."
        )
        st.markdown(
            f"""
            <div class="faq-tab-card">
                <div class="faq-tab-title">
                    <span>🔬</span> {q}
                </div>
                <div class="faq-tab-desc">
                    {a}
                </div>
                <div class="contact-link-row">
                    <span class="contact-link-tag">🎓 TUHH M.Sc. Student</span>
                    <span class="contact-link-tag">🔬 ResearchGate Verified</span>
                    <span class="contact-link-tag">📜 Traffic Sign & Fraud ML Papers</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
