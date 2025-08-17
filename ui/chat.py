# ──────────────────────────────────────────────────────────────────────────────
# file: ui/chat.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Dict, List
import streamlit as st

from services.agentic_ai import AgenticAI
from services.faq import FAQHandler
from services.logger import get_logger

logger = get_logger(__name__)

# Define type alias for readability
ChatHistory = List[Dict[str, str]]

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

# Ensure chat history exists in session state
def _ensure_session_state() -> None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # ✅ fixed: removed invalid annotation


# Process query through FAQ or AI
def _process_user_query(user_query: str, faq_handler: FAQHandler, agent: AgenticAI) -> str:
    q, a = faq_handler.find_similar_question(user_query)
    if a:
        return f"🔍 **FAQ Match:** *{q}*\n\n{a}"
    return agent.generate_response(user_query)


# Render full chat interface
def render_chat(faq_handler: FAQHandler, agent: AgenticAI) -> None:
    _ensure_session_state()

    # Render chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(chat["user_query"])
        with st.chat_message("assistant"):
            st.markdown(chat["bot_response"])

    # User input
    user_query = st.chat_input("What's on your mind ?")

    if user_query:
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.spinner("Let me craft a thoughtful reply just for you... 🤖"):
            response = _process_user_query(user_query, faq_handler, agent)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.chat_history.append(
            {"user_query": user_query, "bot_response": response}
        )

    # Footer / feedback section
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
