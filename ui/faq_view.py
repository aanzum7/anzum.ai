# ──────────────────────────────────────────────────────────────────────────────
# file: ui/faq_view.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Dict, List, Optional
import streamlit as st

def render_faq_multitabs(faq_data: List[Dict], personal_context: Optional[Dict] = None):
    """
    Render high-polish multitab FAQ section with short, punchy cards
    and a prominent '📬 Get In Touch' tab.
    """
    if not faq_data:
        return

    faq_map = {f.get("category", ""): f for f in faq_data}

    # Tab titles
    tabs = st.tabs([
        "🎓 Role & TUHH",
        "💼 Experience",
        "⚡ Skills",
        "🔬 Research",
        "📬 Get In Touch",
    ])

    # 1. Role & TUHH Tab
    with tabs[0]:
        q_obj = faq_map.get("Role", {})
        q = q_obj.get("question", "What is your background and what opportunities are you seeking?")
        a = q_obj.get(
            "answer",
            "Incoming Master's student at Hamburg University of Technology (TUHH) with 5 years in data analytics & applied ML. Actively seeking a Werkstudent opportunity in Data Analytics, BI, Data Engineering, or Applied AI in Hamburg."
        )
        st.markdown(
            f"""
            <div class="faq-tab-card">
                <div class="faq-tab-title">
                    <span>🎓</span> Incoming Master's at TUHH (Hamburg, Germany)
                </div>
                <div class="faq-tab-desc">
                    {a}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("💬 Ask AI about TUHH & Goals", key="tab_btn_role", use_container_width=True):
            st.session_state["queued_prompt"] = q
            st.rerun()

    # 2. Experience Tab
    with tabs[1]:
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
                    <span>💼</span> Brain Station 23 & Prothom Alo Achievements
                </div>
                <div class="faq-tab-desc">
                    {a}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("💬 Ask AI about Experience", key="tab_btn_exp", use_container_width=True):
            st.session_state["queued_prompt"] = q
            st.rerun()

    # 3. Skills Tab
    with tabs[2]:
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
                    <span>⚡</span> Core Technical Skills & Tools
                </div>
                <div class="faq-tab-desc">
                    {a}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("💬 Ask AI about Tech Stack", key="tab_btn_skills", use_container_width=True):
            st.session_state["queued_prompt"] = q
            st.rerun()

    # 4. Research Tab
    with tabs[3]:
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
                    <span>🔬</span> Academic Path & Publications
                </div>
                <div class="faq-tab-desc">
                    {a}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("💬 Ask AI about Research", key="tab_btn_edu", use_container_width=True):
            st.session_state["queued_prompt"] = q
            st.rerun()

    # 5. 📬 Get In Touch Tab
    with tabs[4]:
        st.markdown(
            """
            <div class="faq-tab-card">
                <div class="faq-tab-title">
                    <span>📬</span> Get In Touch & Let's Connect
                </div>
                <div class="faq-tab-desc">
                    Open for <strong>Werkstudent roles in Hamburg</strong>, data analytics collaborations, and AI discussions worldwide.
                </div>
                <div class="contact-link-row">
                    <a href="mailto:tanviranzum70@gmail.com" class="contact-link-tag">
                        <span>📧</span> tanviranzum70@gmail.com
                    </a>
                    <a href="https://www.linkedin.com/in/aanzum/" target="_blank" class="contact-link-tag">
                        <span>💼</span> LinkedIn
                    </a>
                    <a href="https://sites.google.com/view/anzum7/career-highlights" target="_blank" class="contact-link-tag">
                        <span>🌐</span> Highlights
                    </a>
                    <span class="contact-link-tag">
                        <span>📍</span> Hamburg, Germany
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("💬 Say Hello to Tanvir via AI Chat", key="tab_btn_contact", use_container_width=True):
            st.session_state["queued_prompt"] = "Hi Tanvir! I'd love to connect regarding opportunities in Hamburg."
            st.rerun()
