# ──────────────────────────────────────────────────────────────────────────────
# file: app.py
# ──────────────────────────────────────────────────────────────────────────────

import streamlit as st
from services.config import load_configuration, ConfigError
from services.logger import get_logger
from services.agentic_ai import AgenticAI
from services.faq import FAQHandler
from ui.sidebar import render_sidebar
from ui.faq_view import render_faq_tabs
from ui.chat import render_chat

logger = get_logger(__name__)

def build_app():
    """Create and wire up app dependencies."""
    faq_data, personal_context, api_key = load_configuration()
    faq_handler = FAQHandler(faq_data)
    agent = AgenticAI(api_key=api_key, context={"faq": faq_data, "personal": personal_context})
    return faq_handler, agent, faq_data

def main():
    st.set_page_config(page_title="anzum.ai", layout="wide")

    try:
        faq_handler, agent, faq_data = build_app()
    except ConfigError as e:
        st.error(f"Configuration error: {e}")
        logger.exception("Failed to start app due to configuration error.")
        st.stop()
    except Exception as e:
        st.error(f"Startup error: {e}")
        logger.exception("Unexpected error during startup.")
        st.stop()

    # Sidebar
    render_sidebar()

    # FAQ
    st.subheader("💡 Frequently Asked Questions")
    render_faq_tabs(faq_data)

    st.divider()

    # Chat
    st.subheader("💬 Chat with anzum.ai")
    render_chat(faq_handler=faq_handler, agent=agent)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.exception("Application crashed.")

