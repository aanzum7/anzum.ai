# ──────────────────────────────────────────────────────────────────────────────
# file: ui/chat.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Dict, List
import streamlit as st

from config.settings import SUGGESTION_CHIPS, FAQ_SIMILARITY_THRESHOLD, AVATAR_PATH
from services.agentic_ai import AgenticAI
from services.faq import FAQHandler
from services.logger import get_logger

logger = get_logger(__name__)

def _ensure_session_state() -> None:
    """Initialize necessary session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "queued_prompt" not in st.session_state:
        st.session_state.queued_prompt = None
    if "feedback_given" not in st.session_state:
        st.session_state.feedback_given = False

def render_chat(faq_handler: FAQHandler, agent: AgenticAI) -> None:
    """Render the state-of-the-art interactive chat UI with streaming and quick prompt pills."""
    _ensure_session_state()

    # 1. Quick suggestion prompt chips (if history is brief or user wants inspiration)
    st.markdown(
        """
        <div class="chip-label">
            <span>✨</span> Quick Questions to Explore
        </div>
        """,
        unsafe_allow_html=True,
    )

    chip_cols = st.columns(len(SUGGESTION_CHIPS))
    for i, (label, prompt_text) in enumerate(SUGGESTION_CHIPS):
        with chip_cols[i]:
            if st.button(label, key=f"chip_{i}", use_container_width=True):
                st.session_state.queued_prompt = prompt_text
                st.rerun()

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # 2. Render Existing Chat History
    for chat in st.session_state.chat_history:
        with st.chat_message("user", avatar="👤"):
            st.markdown(chat["user_query"])

        with st.chat_message("assistant", avatar=str(AVATAR_PATH)):
            if chat.get("is_faq"):
                st.markdown(
                    f"<div class='faq-match-badge'>✓ Verified Knowledge Base Match: <em>{chat.get('faq_question', '')}</em></div>",
                    unsafe_allow_html=True,
                )
            st.markdown(chat["bot_response"])

    # 3. Determine User Input (Direct Input or Queued Chip)
    user_query = st.chat_input("Ask anything about Tanvir's work, experience, or AI research...")

    if st.session_state.queued_prompt:
        user_query = st.session_state.queued_prompt
        st.session_state.queued_prompt = None

    # 4. Handle Incoming Query
    if user_query:
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)

        # Assistant processing with Streaming or FAQ Match
        with st.chat_message("assistant", avatar=str(AVATAR_PATH)):
            faq_match = faq_handler.find_match_details(user_query, threshold=FAQ_SIMILARITY_THRESHOLD)

            if faq_match:
                q = faq_match["question"]
                a = faq_match["answer"]
                st.markdown(
                    f"<div class='faq-match-badge'>✓ Verified Knowledge Base Match: <em>{q}</em></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(a)
                st.session_state.chat_history.append({
                    "user_query": user_query,
                    "bot_response": a,
                    "is_faq": True,
                    "faq_question": q,
                })
            else:
                # Real-time token streaming
                response_text = st.write_stream(agent.stream_response(user_query))
                st.session_state.chat_history.append({
                    "user_query": user_query,
                    "bot_response": response_text,
                    "is_faq": False,
                })

    # 5. Chat Footer Controls (Feedback & Reset)
    if st.session_state.chat_history:
        st.markdown("<hr style='margin: 28px 0 16px 0; border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
        col_feedback, col_reset = st.columns([2, 1])

        with col_feedback:
            feedback = st.feedback("thumbs", key="chat_feedback")
            if feedback is not None and not st.session_state.feedback_given:
                st.session_state.feedback_given = True
                rating = "Helpful (👍)" if feedback == 1 else "Not Helpful (👎)"
                logger.debug(f"User submitted rating: {rating}")
                st.toast("Thank you for your feedback! 🙏", icon="✨")

        with col_reset:
            if st.button("♻️ Reset Conversation", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.feedback_given = False
                agent.reset()
                st.rerun()
