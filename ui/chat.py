# ──────────────────────────────────────────────────────────────────────────────
# file: ui/chat.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Dict, List, Tuple
import streamlit as st

from services.agentic_ai import AgenticAI
from services.faq import FAQHandler
from services.logger import get_logger

logger = get_logger(__name__)

FOOTER_CSS = """
<style>
.center-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    margin-top: 20px;
}
.center-button {
    width: 50%;
    min-width: 300px;
    padding: 8px 16px;
    background-color: #f0f2f6;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    transition: background-color 0.3s;
}
.center-button:hover { background-color: #e0e2e6; }
</style>
"""

def _ensure_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history: List[Dict[str, str]] = []

def _process_user_query(user_query: str, faq_handler: FAQHandler, agent: AgenticAI) -> str:
    q, a = faq_handler.find_similar_question(user_query)
    if a:
        return f"🔍 **FAQ Match:** *{q}*\n\n{a}"
    return agent.generate_response(user_query)

def render_chat(faq_handler: FAQHandler, agent: AgenticAI):
    _ensure_session_state()

    # Render existing history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(chat["user_query"])
        with st.chat_message("assistant"):
            st.markdown(chat["bot_response"])

    # Input
    user_query = st.chat_input("What's on your mind ?")

    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.spinner("Let me craft a thoughtful reply just for you... 🤖"):
            response = _process_user_query(user_query, faq_handler, agent)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.chat_history.append({"user_query": user_query, "bot_response": response})

    # Footer / feedback
    st.markdown(FOOTER_CSS, unsafe_allow_html=True)

    if st.session_state.chat_history:
        st.markdown("<div class='center-container'>", unsafe_allow_html=True)

        feedback = st.radio(
            "Feedback",
            ["👍", "👎"],
            index=None,
            horizontal=True,
            key="overall_feedback",
        )
        if feedback:
            logger.info(f"Overall Feedback: {feedback}")

        if st.button("♻️ Start Over", use_container_width=True):
            st.session_state.chat_history = []
            agent.reset()
            st.rerun()

