# ──────────────────────────────────────────────────────────────────────────────
# file: aanzum.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import streamlit as st

from config.settings import APP_TITLE, APP_ICON
from services.config import load_configuration, ConfigError
from services.logger import get_logger
from services.agentic_ai import AgenticAI
from services.faq import FAQHandler
from services.mcp_server import create_mcp_server
from ui.styles import inject_styles
from ui.sidebar import render_sidebar
from ui.faq_view import render_faq_multitabs
from ui.chat import render_chat

logger = get_logger(__name__)

def build_app():
    """Create and wire up app dependencies with session persistence."""
    faq_data, personal_context, api_key = load_configuration()
    faq_handler = FAQHandler(faq_data)
    mcp_server = create_mcp_server(personal_context=personal_context, faq_data=faq_data)

    # Cache agent instance in session_state to preserve multi-turn conversation memory
    if "agent" not in st.session_state:
        st.session_state.agent = AgenticAI(
            api_key=api_key,
            context={"faq": faq_data, "personal": personal_context},
            mcp_server=mcp_server,
        )

    return faq_handler, st.session_state.agent, faq_data, personal_context

def render_hero_banner(model_label: str = "Gemini Multi-Model"):
    """Render compact, modern glassmorphism hero banner."""
    st.markdown(
        f"""
        <div class="hero-container" style="padding: 22px 28px; margin-bottom: 18px;">
            <div class="hero-title-row">
                <div class="hero-title" style="font-size: 2.1rem;">
                    <span>Hey, I'm</span>
                    <span class="brand-gradient">anzum.ai</span>
                    <span style="font-size: 1.6rem;">⚡</span>
                </div>
                <div class="hero-badge-pill" title="MCP Knowledge Server & Multi-Model Failover Active">
                    <span class="pulse-dot"></span>
                    <span>AI Twin • {model_label} • MCP Agent</span>
                </div>
            </div>
            <p class="hero-desc" style="font-size: 0.98rem; margin-top: 8px; line-height: 1.6;">
                Incoming <strong>M.Sc. Student at TUHH (Hamburg)</strong> actively seeking a <strong>Werkstudent position</strong> in Data Analytics & Applied AI — backed by 5+ years building production recommendation engines at <strong>Prothom Alo</strong> & <strong>Brain Station 23</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject global design system tokens
    inject_styles()

    try:
        faq_handler, agent, faq_data, personal_context = build_app()
    except ConfigError as e:
        st.error(f"Configuration error: {e}")
        logger.exception("Failed to start app due to configuration error.")
        st.stop()
    except Exception as e:
        st.error(f"Startup error: {e}")
        logger.exception("Unexpected error during startup.")
        st.stop()

    # Dynamic Sidebar (Profile avatar, roles, social links)
    render_sidebar(personal_context=personal_context, active_model_label=agent.active_model_label)

    # Hero Banner
    render_hero_banner(model_label=agent.active_model_label)

    # Main App Navigation: Dedicated Chat Tab & Interactive FAQ Subtabs
    tab_chat, tab_faq = st.tabs([
        "✨ AI Twin Chat",
        "📖 FAQ",
    ])

    with tab_chat:
        render_chat(agent=agent)

    with tab_faq:
        render_faq_multitabs(faq_data=faq_data, personal_context=personal_context)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.exception("Application crashed.")
