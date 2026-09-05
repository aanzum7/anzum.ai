from __future__ import annotations

from datetime import datetime
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
    Render dedicated conversational AI Twin Chat interface with descending time order.
    Features:
      - Descending time order (latest message displayed at the top)
      - Formatted timestamp on each turn (hh:mm AM/PM)
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

    # 2. Determine User Input (Direct Input or Queued Chip/Regenerate)
    user_query = st.chat_input("Ask anything about Tanvir's work, experience, or AI research...")

    if st.session_state.queued_prompt:
        user_query = st.session_state.queued_prompt
        st.session_state.queued_prompt = None

    # 3. Descending Timeline Indicator
    if st.session_state.chat_history or user_query:
        st.markdown(
            "<div style='display: flex; justify-content: space-between; align-items: center; margin: 14px 0 12px 0;'>"
            "<span style='font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>AI Twin Conversation</span>"
            "<span style='font-size: 10.5px; color: #818CF8; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); padding: 2px 8px; border-radius: 4px;'>↓ Newest First</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    # 4. Upper-side slot for the newest incoming message
    active_turn_slot = st.container()
    new_turn_added = False

    if user_query:
        now_time = datetime.now().strftime("%I:%M %p")
        with active_turn_slot:
            with st.chat_message("user", avatar="👤"):
                st.markdown(
                    f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
                    f"<span style='font-weight:600; font-size:13px; color:#F1F5F9;'>You</span>"
                    f"<span style='font-size:11px; color:#64748B; font-family:monospace;'>{now_time}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(user_query)

            # Anti-abuse / rate limit check per single chat & device
            is_allowed, funky_limit_msg = limiter.check_rate_limit(client_id)

            if not is_allowed and funky_limit_msg:
                # Display playful funky rate limit warning directly in chat
                with st.chat_message("assistant", avatar=str(AVATAR_PATH)):
                    st.markdown(
                        f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
                        f"<span style='font-weight:600; font-size:13px; color:#818CF8;'>Tanvir • AI Twin</span>"
                        f"<span style='font-size:11px; color:#64748B; font-family:monospace;'>{now_time}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(funky_limit_msg)
                st.session_state.chat_history.insert(0, {
                    "user_query": user_query,
                    "bot_response": funky_limit_msg,
                    "time": now_time,
                })
            else:
                # Process query via AI Twin with semantic caching & failover
                with st.chat_message("assistant", avatar=str(AVATAR_PATH)):
                    st.markdown(
                        f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
                        f"<span style='font-weight:600; font-size:13px; color:#818CF8;'>Tanvir • AI Twin</span>"
                        f"<span style='font-size:11px; color:#64748B; font-family:monospace;'>{now_time}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    try:
                        response_text = st.write_stream(agent.stream_response(user_query))
                    except Exception as e:
                        logger.error(f"Background chat stream exception: {e}")
                        funky_fallback = get_funky_glitch_response()
                        st.markdown(funky_fallback)
                        response_text = funky_fallback

                st.session_state.chat_history.insert(0, {
                    "user_query": user_query,
                    "bot_response": response_text,
                    "time": now_time,
                })
        new_turn_added = True

    # 5. Render Prior Conversation History in Descending Order (Newest to Oldest)
    past_messages = st.session_state.chat_history[1:] if new_turn_added else st.session_state.chat_history

    for chat in past_messages:
        t = chat.get("time", "")
        with st.chat_message("user", avatar="👤"):
            if t:
                st.markdown(
                    f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
                    f"<span style='font-weight:600; font-size:13px; color:#F1F5F9;'>You</span>"
                    f"<span style='font-size:11px; color:#64748B; font-family:monospace;'>{t}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(chat["user_query"])

        with st.chat_message("assistant", avatar=str(AVATAR_PATH)):
            if t:
                st.markdown(
                    f"<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;'>"
                    f"<span style='font-weight:600; font-size:13px; color:#818CF8;'>Tanvir • AI Twin</span>"
                    f"<span style='font-size:11px; color:#64748B; font-family:monospace;'>{t}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(chat["bot_response"])

    # 6. Chat Footer Controls: Like/Dislike in a single row (Left/Right) + Full-Width Clear
    if st.session_state.chat_history:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

        # Row 1: Like (Left) and Dislike (Right) in a single row
        col_like, col_dislike = st.columns(2)
        with col_like:
            if st.button("👍 Helpful", key="btn_chat_like", use_container_width=True):
                st.toast("Thank you for your feedback! 👍", icon="✨")
        with col_dislike:
            if st.button("👎 Needs Improvement", key="btn_chat_dislike", use_container_width=True):
                st.toast("Feedback noted. I will keep improving! 💬", icon="📝")

        # Row 2: Full-width button for Clear Conversation
        if st.button("🗑️ Clear Conversation", key="btn_clear_chat_full", use_container_width=True):
            limiter.reset_client(client_id)
            st.session_state.chat_history = []
            st.session_state.queued_prompt = None
            agent.reset()
            st.rerun()
