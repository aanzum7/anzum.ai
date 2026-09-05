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

def render_sidebar(personal_context: Optional[Dict[str, Any]] = None, active_model_label: Optional[str] = None):
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

        st.markdown("<hr style='margin: 10px 0 14px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

        # 🎯 Focused Current Status (Compact, high impact, no long paragraphs)
        st.markdown(
            """
            <div class="sidebar-current-card">
                <div class="current-item">
                    <span class="current-badge">🎓 Current</span>
                    <div class="current-title">M.Sc. Student @ TUHH</div>
                    <div class="current-sub">Hamburg University of Technology</div>
                </div>
                <div class="current-item">
                    <span class="current-badge seeking">🔍 Seeking</span>
                    <div class="current-title">Werkstudent (Data / AI / BI)</div>
                    <div class="current-sub">Hamburg, Germany & Remote</div>
                </div>
            </div>
            <div class="sidebar-pill-row">
                <span class="status-pill">📍 Hamburg, DE</span>
                <span class="status-pill">⚡ 5+ Yrs Exp</span>
                <span class="status-pill">🤖 RecSys & ML</span>
                <span class="status-pill">📊 BI & Analytics</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Professional Links Grid (LinkedIn and ResearchGate)
        linkedin_url = prof_links.get("linkedin", "https://www.linkedin.com/in/aanzum/")
        rg_url = prof_links.get("researchgate", "https://www.researchgate.net/profile/Tanvir-Anzum")

        st.markdown(
            f"""
            <div class="link-grid">
                <a href="{linkedin_url}" target="_blank" class="link-btn">
                    <span>💼</span> LinkedIn
                </a>
                <a href="{rg_url}" target="_blank" class="link-btn">
                    <span>🔬</span> ResearchGate
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Prominent Get In Touch Card (Email & Phone with icons - best way)
        email = contact.get("email", "tanviranzum70@gmail.com")
        phone = contact.get("phone", "+88-016-87153529")
        clean_phone = phone.replace("-", "").replace(" ", "")

        st.markdown(
            f"""
            <div class="sidebar-contact-card">
                <div class="contact-card-header">📬 Get In Touch</div>
                <a href="mailto:{email}" class="contact-item-row" title="Send direct email">
                    <span class="contact-icon">📧</span>
                    <div class="contact-details">
                        <span class="contact-label">Email</span>
                        <span class="contact-val">{email}</span>
                    </div>
                </a>
                <a href="tel:{clean_phone}" class="contact-item-row" title="Call or WhatsApp">
                    <span class="contact-icon">📱</span>
                    <div class="contact-details">
                        <span class="contact-label">Phone</span>
                        <span class="contact-val">{phone}</span>
                    </div>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

        model_display = active_model_label or "Gemini Multi-Model"
        st.markdown(
            f"""
            <div style='text-align: center; margin-top: 18px; font-size: 0.72rem; color: #64748B;'>
                anzum.ai v{APP_VERSION} • {model_display}
            </div>
            """,
            unsafe_allow_html=True,
        )
