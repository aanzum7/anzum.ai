# ──────────────────────────────────────────────────────────────────────────────
# file: ui/chat.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Any, Dict, List, Optional
import uuid
import streamlit as st

from config.settings import SUGGESTION_CHIPS, AVATAR_PATH
from services.agentic_ai import AgenticAI
from services.logger import get_logger
from services.rate_limiter import get_rate_limiter, get_funky_glitch_response

logger = get_logger(__name__)

def _get_client_id() -> str:
    """
    Generate or retrieve a unique, persistent client device/session identifier.
    Uses reverse proxy client IP if present, falling back to a session UUID.
    """
    if "_client_device_id" not in st.session_state:
        st.session_state._client_device_id = str(uuid.uuid4())

    try:
        ctx = getattr(st, "context", None)
        if ctx and hasattr(ctx, "headers"):
            headers = ctx.headers
            fwd = headers.get("x-forwarded-for") or headers.get("remote-addr")
            if fwd:
                return fwd.split(",")[0].strip()
    except Exception:
        pass

    return st.session_state._client_device_id

def _ensure_session_state() -> None:
    """Initialize necessary session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "queued_prompt" not in st.session_state:
        st.session_state.queued_prompt = None


def render_chat(agent: AgenticAI, faq_handler: Optional[Any] = None) -> None:
    """
    Render dedicated conversational AI Twin Chat interface.
    Features:
      - Device/session rate limiting & anti-abuse protection
      - Semantic cache lookup for fast, token-free answers to similar queries
      - Silent background error handling with zero technical error leaks
      - Funky, witty fallback responses
      - Like/dislike feedback & full-width clear conversation button
    """
    _ensure_session_state()
    limiter = get_rate_limiter()
    client_id = _get_client_id()

    # 1. Quick suggestion prompt chips
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
            st.markdown(chat["bot_response"])

    # 3. Determine User Input (Direct Input or Queued Chip/Regenerate)
    user_query = st.chat_input("Ask anything about Tanvir's work, experience, or AI research...")

    if st.session_state.queued_prompt:
        user_query = st.session_state.queued_prompt
        st.session_state.queued_prompt = None

    # 4. Handle Incoming Query
    if user_query:
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)

        # Anti-abuse / rate limit check per single chat & device
        is_allowed, funky_limit_msg = limiter.check_rate_limit(client_id)

        if not is_allowed and funky_limit_msg:
            # Display playful funky rate limit warning directly in chat
            with st.chat_message("assistant", avatar=str(AVATAR_PATH)):
                st.markdown(funky_limit_msg)
        else:
            # Process query via AI Twin with semantic caching & failover
            with st.chat_message("assistant", avatar=str(AVATAR_PATH)):
                try:
                    response_text = st.write_stream(agent.stream_response(user_query))
                except Exception as e:
                    logger.error(f"Background chat stream exception: {e}")
                    # Show funky, charming fallback instead of scary error logs
                    funky_fallback = get_funky_glitch_response()
                    st.markdown(funky_fallback)
                    response_text = funky_fallback

                st.session_state.chat_history.append({
                    "user_query": user_query,
                    "bot_response": response_text,
                })

    # 5. Chat Footer Controls: Like/Dislike in a single row (Left/Right) + Full-Width Clear
    if st.session_state.chat_history:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        # Row 1: Like (Left) and Dislike (Right) in a single row
        col_like, col_dislike = st.columns(2)
        with col_like:
            if st.button("👍 Helpful", key="btn_chat_like", use_container_width=True):
                st.toast("Thank you for your feedback! 👍", icon="✨")
        with col_dislike:
            if st.button("👎 Needs Improvement", key="btn_chat_dislike", use_container_width=True):
                st.toast("Feedback noted. I will keep improving! 🙏", icon="📝")

        # Row 2: Full-width button for Clear Conversation
        if st.button("🗑️ Clear Conversation", key="btn_clear_chat_full", use_container_width=True):
            limiter.reset_client(client_id)
            st.session_state.chat_history = []
            st.session_state.queued_prompt = None
            agent.reset()
            st.rerun()
