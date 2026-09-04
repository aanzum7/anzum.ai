# ──────────────────────────────────────────────────────────────────────────────
# file: ui/sidebar.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import base64
import os
from typing import Any, Dict, Optional
import streamlit as st

from config.settings import AVATAR_PATH, APP_VERSION, DEFAULT_GEMINI_MODEL, AUTHOR, APP_SUBTITLE

def _get_image_base64(filepath) -> Optional[str]:
    """Convert local image file to base64 data URI."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:image/png;base64,{encoded}"
        except Exception:
            return None
    return None

def render_sidebar(personal_context: Optional[Dict[str, Any]] = None):
    """Render high-polish profile sidebar with dynamic context and link buttons."""
    data = personal_context or {}
    avatar_b64 = _get_image_base64(AVATAR_PATH)

    current_role = data.get("professional_current_role", "Data Analytics & Applied AI Professional")
    social_links = data.get("social_links", {})
    prof_links = data.get("professional_links", {})
    contact = data.get("contact", {})
    education = data.get("education_summary", "")

    with st.sidebar:
        # Avatar & Profile Header
        avatar_html = f'<img src="{avatar_b64}" alt="Tanvir Anzum">' if avatar_b64 else '<div style="font-size: 40px; padding: 20px;">👨‍💻</div>'
        st.markdown(
            f"""
            <div class="sidebar-avatar-container">
                <div class="avatar-wrapper">
                    {avatar_html}
                </div>
                <div class="sidebar-name">Tanvir Anzum</div>
                <div class="sidebar-title-caption">{APP_SUBTITLE}</div>
                <div class="sidebar-status-tag">
                    <span class="pulse-dot"></span>
                    <span>AI Twin Online</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Current Role Card
        st.markdown(
            f"""
            <div class="sidebar-card">
                <div class="sidebar-card-title">💼 Current Focus</div>
                <div class="sidebar-card-body">{current_role}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Education Summary (if present)
        if education:
            st.markdown(
                f"""
                <div class="sidebar-card">
                    <div class="sidebar-card-title">🎓 Education</div>
                    <div class="sidebar-card-body">{education}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Professional Links Grid
        st.markdown("<div class='sidebar-card-title' style='margin-top: 14px;'>🌐 Professional Links</div>", unsafe_allow_html=True)
        
        linkedin_url = prof_links.get("linkedin", "https://www.linkedin.com/in/aanzum/")
        github_url = prof_links.get("github", "https://github.com/aanzum7")
        rg_url = prof_links.get("researchgate", "https://www.researchgate.net/profile/Tanvir-Anzum")
        streamlit_url = prof_links.get("streamlit", "https://share.streamlit.io/user/aanzum7")
        portfolio_url = social_links.get("personal_site", "https://sites.google.com/view/anzum7")

        st.markdown(
            f"""
            <div class="link-grid">
                <a href="{linkedin_url}" target="_blank" class="link-btn">
                    <span>💼</span> LinkedIn
                </a>
                <a href="{github_url}" target="_blank" class="link-btn">
                    <span>💻</span> GitHub
                </a>
                <a href="{rg_url}" target="_blank" class="link-btn">
                    <span>🔬</span> Research
                </a>
                <a href="{streamlit_url}" target="_blank" class="link-btn">
                    <span>⚡</span> Apps
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Direct Contact Expander
        with st.expander("📬 Get In Touch"):
            email = contact.get("email", "tanviranzum70@gmail.com")
            edu_email = contact.get("edu_email", "")
            phone = contact.get("phone", "")

            st.markdown(f"**Email:** [{email}](mailto:{email})")
            if edu_email:
                st.markdown(f"**Academic:** [{edu_email}](mailto:{edu_email})")
            if phone:
                st.markdown(f"**Phone:** `{phone}`")
            if portfolio_url:
                st.markdown(f"**Portfolio:** [anzum7 Website]({portfolio_url})")

        st.markdown(
            f"""
            <div style='text-align: center; margin-top: 24px; font-size: 0.75rem; color: #64748B;'>
                anzum.ai v{APP_VERSION} • Powered by Gemini 2.5 Flash
            </div>
            """,
            unsafe_allow_html=True,
        )
