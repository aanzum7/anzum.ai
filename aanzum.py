"""
anzum.ai — Personal AI Agent
Gemini-style multi-tab interactive design, single-file Streamlit app.
"""

import streamlit as st
import anthropic
import json
import os
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# CONFIG & CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

PAGE_TITLE = "anzum.ai"
PAGE_ICON = "✦"
MODEL = "claude-opus-4-5"

FAQ_DATA: dict[str, list[dict]] = {
    "About Me": [
        {
            "q": "Who are you?",
            "a": "I'm Anzum — a software engineer, builder, and curious mind. I work on AI-powered products and love turning ideas into reality.",
        },
        {
            "q": "What do you do?",
            "a": "I build web apps, AI agents, and developer tools. Currently focused on LLM integrations and agentic workflows.",
        },
    ],
    "Skills": [
        {
            "q": "What technologies do you work with?",
            "a": "Python, TypeScript, React, FastAPI, Streamlit, LangChain, Anthropic Claude, OpenAI, Docker, and more.",
        },
        {
            "q": "Do you do freelance work?",
            "a": "Yes! I'm available for interesting projects. Reach out via the contact form.",
        },
    ],
    "Projects": [
        {
            "q": "What have you built?",
            "a": "AI chatbots, agentic pipelines, SaaS tools, and open-source libraries. Check the Projects tab for details.",
        },
    ],
}

PERSONAL_CONTEXT = """
You are anzum.ai — the personal AI agent of Anzum.
You represent Anzum online: a software engineer who builds AI-powered products.
Be helpful, concise, and friendly. Speak in first person as Anzum when appropriate.
Never make up facts. If unsure, say so and offer to help find the answer.
"""

PROJECTS = [
    {
        "name": "anzum.ai",
        "desc": "Personal AI agent with agentic capabilities, FAQ, and chat interface.",
        "tags": ["Python", "Streamlit", "Claude"],
        "icon": "✦",
        "color": "#7C3AED",
        "link": "#",
    },
    {
        "name": "AgenFlow",
        "desc": "Visual builder for LLM agentic workflows with drag-and-drop nodes.",
        "tags": ["React", "TypeScript", "LangChain"],
        "icon": "⬡",
        "color": "#0EA5E9",
        "link": "#",
    },
    {
        "name": "DocuMind",
        "desc": "RAG-powered document Q&A system with multi-format ingestion.",
        "tags": ["Python", "FastAPI", "Chroma"],
        "icon": "◈",
        "color": "#10B981",
        "link": "#",
    },
    {
        "name": "CodeSight",
        "desc": "AI code reviewer that explains, refactors, and documents your codebase.",
        "tags": ["Claude", "GitHub", "Actions"],
        "icon": "◉",
        "color": "#F59E0B",
        "link": "#",
    },
]

SKILLS_DATA = {
    "AI / LLM": ["Claude API", "OpenAI", "LangChain", "RAG", "Embeddings", "Agents"],
    "Backend": ["Python", "FastAPI", "Django", "PostgreSQL", "Redis", "Docker"],
    "Frontend": ["React", "TypeScript", "Streamlit", "Next.js", "Tailwind CSS"],
    "Tools": ["Git", "GitHub Actions", "Vercel", "AWS", "Supabase", "Pinecone"],
}

QUICK_PROMPTS = [
    "What projects have you built?",
    "What's your tech stack?",
    "Are you available for freelance?",
    "Tell me about your AI experience.",
    "How can I contact you?",
]


# ──────────────────────────────────────────────────────────────────────────────
# GEMINI-STYLE CSS
# ──────────────────────────────────────────────────────────────────────────────

GEMINI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600&family=Google+Sans+Mono&display=swap');

:root {
    --gem-bg: #0f0f0f;
    --gem-surface: #1a1a1a;
    --gem-surface-2: #222222;
    --gem-border: rgba(255,255,255,0.08);
    --gem-border-hover: rgba(255,255,255,0.16);
    --gem-text: #e8eaed;
    --gem-muted: #9aa0a6;
    --gem-accent: #8ab4f8;
    --gem-accent-2: #a78bfa;
    --gem-accent-3: #34d399;
    --gem-gradient: linear-gradient(135deg, #8ab4f8 0%, #a78bfa 50%, #f472b6 100%);
    --gem-radius: 16px;
    --gem-radius-sm: 10px;
    --font: 'Google Sans', 'Segoe UI', sans-serif;
    --font-mono: 'Google Sans Mono', monospace;
}

/* ── Global Reset ── */
html, body, [class*="st-"] {
    font-family: var(--font) !important;
}

.stApp {
    background: var(--gem-bg) !important;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, header, footer { display: none !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Custom Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--gem-bg); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 3px; }

/* ── NAV BAR ── */
.gem-nav {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(15,15,15,0.92);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--gem-border);
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
}

.gem-logo {
    background: var(--gem-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.5px;
}

.gem-nav-links {
    display: flex;
    gap: 4px;
}

.gem-nav-link {
    color: var(--gem-muted);
    font-size: 14px;
    font-weight: 500;
    padding: 8px 16px;
    border-radius: 24px;
    cursor: pointer;
    border: none;
    background: transparent;
    transition: all 0.2s;
    font-family: var(--font);
}

.gem-nav-link:hover {
    background: var(--gem-surface-2);
    color: var(--gem-text);
}

.gem-nav-link.active {
    background: rgba(138, 180, 248, 0.12);
    color: var(--gem-accent);
}

/* ── HERO SECTION ── */
.gem-hero {
    padding: 80px 40px 60px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.gem-hero::before {
    content: '';
    position: absolute;
    top: -120px;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    height: 600px;
    background: radial-gradient(ellipse, rgba(138,180,248,0.06) 0%, transparent 70%);
    pointer-events: none;
}

.gem-avatar {
    width: 80px;
    height: 80px;
    margin: 0 auto 24px;
    border-radius: 50%;
    background: var(--gem-gradient);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    color: #fff;
    font-weight: 600;
    position: relative;
}

.gem-avatar::after {
    content: '';
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    background: var(--gem-gradient);
    z-index: -1;
    opacity: 0.4;
    filter: blur(8px);
}

.gem-hero-title {
    font-size: 48px;
    font-weight: 600;
    line-height: 1.15;
    letter-spacing: -1px;
    margin: 0 0 16px;
    background: var(--gem-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gem-hero-sub {
    font-size: 18px;
    color: var(--gem-muted);
    max-width: 520px;
    margin: 0 auto 40px;
    line-height: 1.6;
}

.gem-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(52, 211, 153, 0.1);
    border: 1px solid rgba(52, 211, 153, 0.25);
    color: var(--gem-accent-3);
    font-size: 13px;
    font-weight: 500;
    padding: 6px 16px;
    border-radius: 24px;
    margin-bottom: 24px;
}

.gem-status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--gem-accent-3);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.3); }
}

/* ── QUICK PROMPT CHIPS ── */
.gem-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
    margin: 0 auto 48px;
    max-width: 700px;
}

.gem-chip {
    background: var(--gem-surface);
    border: 1px solid var(--gem-border);
    color: var(--gem-text);
    font-size: 13.5px;
    font-weight: 400;
    padding: 9px 18px;
    border-radius: 24px;
    cursor: pointer;
    transition: all 0.2s;
    font-family: var(--font);
}

.gem-chip:hover {
    background: var(--gem-surface-2);
    border-color: var(--gem-border-hover);
    color: var(--gem-accent);
    transform: translateY(-1px);
}

/* ── CHAT CONTAINER ── */
.gem-chat-wrap {
    max-width: 780px;
    margin: 0 auto;
    padding: 0 24px 40px;
}

.gem-input-card {
    background: var(--gem-surface);
    border: 1px solid var(--gem-border);
    border-radius: var(--gem-radius);
    padding: 4px 8px 8px;
    transition: border-color 0.2s;
    margin-bottom: 24px;
}

.gem-input-card:focus-within {
    border-color: rgba(138,180,248,0.4);
    box-shadow: 0 0 0 3px rgba(138,180,248,0.06);
}

/* ── MESSAGE BUBBLES ── */
.gem-msg {
    margin-bottom: 24px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}

.gem-msg-icon {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
    font-weight: 600;
}

.gem-msg-icon.user {
    background: rgba(138,180,248,0.15);
    color: var(--gem-accent);
}

.gem-msg-icon.agent {
    background: var(--gem-gradient);
    color: #fff;
}

.gem-msg-body {
    flex: 1;
    padding-top: 6px;
}

.gem-msg-name {
    font-size: 12px;
    font-weight: 600;
    color: var(--gem-muted);
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 6px;
}

.gem-msg-text {
    font-size: 15px;
    color: var(--gem-text);
    line-height: 1.7;
}

.gem-msg-text code {
    font-family: var(--font-mono);
    background: rgba(255,255,255,0.06);
    padding: 2px 6px;
    border-radius: 5px;
    font-size: 13px;
}

/* ── SECTION HEADING ── */
.gem-section-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--gem-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 40px 0 20px;
    padding: 0 40px;
}

/* ── FAQ CARDS ── */
.gem-faq-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 16px;
    padding: 0 40px;
    max-width: 1200px;
    margin: 0 auto 48px;
}

.gem-faq-card {
    background: var(--gem-surface);
    border: 1px solid var(--gem-border);
    border-radius: var(--gem-radius);
    padding: 24px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}

.gem-faq-card:hover {
    background: var(--gem-surface-2);
    border-color: var(--gem-border-hover);
    transform: translateY(-2px);
}

.gem-faq-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--gem-gradient);
    opacity: 0;
    transition: opacity 0.2s;
}

.gem-faq-card:hover::before { opacity: 1; }

.gem-faq-q {
    font-size: 15px;
    font-weight: 500;
    color: var(--gem-text);
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
}

.gem-faq-icon {
    background: linear-gradient(135deg, rgba(138,180,248,0.15), rgba(167,139,250,0.15));
    border-radius: 8px;
    width: 28px; height: 28px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
    margin-top: 1px;
}

.gem-faq-a {
    font-size: 14px;
    color: var(--gem-muted);
    line-height: 1.65;
    padding-left: 38px;
}

/* ── PROJECT CARDS ── */
.gem-project-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    padding: 0 40px;
    max-width: 1200px;
    margin: 0 auto 48px;
}

.gem-project-card {
    background: var(--gem-surface);
    border: 1px solid var(--gem-border);
    border-radius: var(--gem-radius);
    padding: 28px;
    transition: all 0.25s;
    position: relative;
    overflow: hidden;
}

.gem-project-card:hover {
    background: var(--gem-surface-2);
    border-color: var(--gem-border-hover);
    transform: translateY(-3px);
}

.gem-project-icon {
    font-size: 28px;
    margin-bottom: 16px;
    display: block;
}

.gem-project-name {
    font-size: 17px;
    font-weight: 600;
    color: var(--gem-text);
    margin-bottom: 8px;
}

.gem-project-desc {
    font-size: 14px;
    color: var(--gem-muted);
    line-height: 1.6;
    margin-bottom: 20px;
}

.gem-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
}

.gem-tag {
    background: rgba(138,180,248,0.1);
    border: 1px solid rgba(138,180,248,0.2);
    color: var(--gem-accent);
    font-size: 11.5px;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 20px;
}

/* ── SKILLS ── */
.gem-skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
    padding: 0 40px;
    max-width: 1200px;
    margin: 0 auto 48px;
}

.gem-skill-group {
    background: var(--gem-surface);
    border: 1px solid var(--gem-border);
    border-radius: var(--gem-radius);
    padding: 24px;
}

.gem-skill-group-title {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
    background: var(--gem-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.gem-skill-badge {
    display: inline-block;
    background: var(--gem-surface-2);
    border: 1px solid var(--gem-border);
    color: var(--gem-text);
    font-size: 12.5px;
    padding: 4px 12px;
    border-radius: 8px;
    margin: 4px 4px 4px 0;
    font-family: var(--font-mono);
}

/* ── CONTACT FORM ── */
.gem-contact-wrap {
    max-width: 560px;
    margin: 0 auto;
    padding: 0 40px 60px;
}

/* ── STREAMLIT INPUT OVERRIDES ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: transparent !important;
    border: none !important;
    color: var(--gem-text) !important;
    font-family: var(--font) !important;
    font-size: 15px !important;
    box-shadow: none !important;
    caret-color: var(--gem-accent) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    box-shadow: none !important;
    border: none !important;
    outline: none !important;
}

.stButton > button {
    background: var(--gem-gradient) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 24px !important;
    font-family: var(--font) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 10px 28px !important;
    transition: opacity 0.2s, transform 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* Divider */
.gem-divider {
    height: 1px;
    background: var(--gem-border);
    margin: 8px 0 32px;
}

/* Tab bar override */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 0 !important;
    border-bottom: 1px solid var(--gem-border) !important;
    padding: 0 40px !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--gem-muted) !important;
    font-family: var(--font) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 14px 20px !important;
    border-radius: 0 !important;
    transition: all 0.2s !important;
}

.stTabs [aria-selected="true"] {
    color: var(--gem-accent) !important;
    border-bottom-color: var(--gem-accent) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 0 !important;
}

/* Typing indicator */
.gem-typing {
    display: flex;
    gap: 5px;
    align-items: center;
    padding: 6px 0;
}

.gem-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--gem-accent);
    animation: bounce 1.2s infinite;
}
.gem-dot:nth-child(2) { animation-delay: 0.2s; }
.gem-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
    40% { transform: translateY(-5px); opacity: 1; }
}

/* Stat row */
.gem-stats {
    display: flex;
    gap: 32px;
    justify-content: center;
    margin: 48px 0 16px;
}

.gem-stat {
    text-align: center;
}

.gem-stat-num {
    font-size: 32px;
    font-weight: 600;
    background: var(--gem-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}

.gem-stat-label {
    font-size: 12px;
    color: var(--gem-muted);
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* Footer */
.gem-footer {
    text-align: center;
    padding: 32px 40px;
    border-top: 1px solid var(--gem-border);
    color: var(--gem-muted);
    font-size: 13px;
}

.gem-footer a { color: var(--gem-accent); text-decoration: none; }

/* Alert */
.gem-alert {
    background: rgba(52,211,153,0.07);
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: var(--gem-radius-sm);
    padding: 14px 18px;
    color: var(--gem-accent-3);
    font-size: 14px;
    margin-bottom: 20px;
}
</style>
"""


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    """Resolve Anthropic API key from secrets or env."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            st.error("⚠️ ANTHROPIC_API_KEY not found. Add it to .streamlit/secrets.toml or as an env variable.")
            st.stop()
        return key


def get_client() -> anthropic.Anthropic:
    if "client" not in st.session_state:
        st.session_state.client = anthropic.Anthropic(api_key=get_api_key())
    return st.session_state.client


def init_session():
    """Initialise all session-state keys once."""
    defaults = {
        "messages": [],           # chat history
        "tab": "Chat",            # active tab
        "contact_sent": False,    # form submitted flag
        "faq_expanded": {},       # {key: bool}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def faq_match(user_msg: str) -> str | None:
    """Return a canned FAQ answer if the question closely matches one."""
    msg_lower = user_msg.lower()
    for _cat, items in FAQ_DATA.items():
        for item in items:
            keywords = re.findall(r"\w+", item["q"].lower())
            if sum(1 for w in keywords if w in msg_lower) >= max(1, len(keywords) // 2):
                return item["a"]
    return None


def stream_response(messages: list[dict]) -> str:
    """Call Claude with streaming; return full assistant text."""
    client = get_client()
    full = ""
    placeholder = st.empty()
    with client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        system=PERSONAL_CONTEXT,
        messages=messages,
    ) as stream:
        for chunk in stream.text_stream:
            full += chunk
            # render incrementally with cursor
            placeholder.markdown(
                f'<div class="gem-msg-text">{full}▌</div>',
                unsafe_allow_html=True,
            )
    placeholder.markdown(
        f'<div class="gem-msg-text">{full}</div>',
        unsafe_allow_html=True,
    )
    return full


# ──────────────────────────────────────────────────────────────────────────────
# UI SECTIONS
# ──────────────────────────────────────────────────────────────────────────────

def render_navbar():
    tabs = ["Chat", "About", "Projects", "Skills", "Contact"]
    active = st.session_state.tab

    links_html = "".join(
        f'<span class="gem-nav-link {"active" if t == active else ""}">{t}</span>'
        for t in tabs
    )

    st.markdown(
        f"""
        <nav class="gem-nav">
            <span class="gem-logo">✦ anzum.ai</span>
            <div class="gem-nav-links">{links_html}</div>
        </nav>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="gem-hero">
            <div class="gem-avatar">A</div>
            <div class="gem-status-pill">
                <div class="gem-status-dot"></div>
                Available for projects
            </div>
            <h1 class="gem-hero-title">Hi, I'm Anzum</h1>
            <p class="gem-hero-sub">
                Software engineer building AI-powered products, agentic workflows,
                and developer tools that actually work.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_prompts():
    """Render clickable chip buttons that inject a prompt into the chat."""
    cols = st.columns(len(QUICK_PROMPTS))
    for col, prompt in zip(cols, QUICK_PROMPTS):
        with col:
            if st.button(prompt, key=f"chip_{prompt}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()


# ── CHAT TAB ──────────────────────────────────────────────────────────────────

def render_chat_tab():
    render_hero()

    st.markdown('<p style="text-align:center;color:var(--gem-muted);font-size:13px;margin:-20px 0 16px;">Try asking me something →</p>', unsafe_allow_html=True)
    render_quick_prompts()

    st.markdown('<div class="gem-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="gem-chat-wrap">', unsafe_allow_html=True)

    # ── Message history ──
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            st.markdown(
                f"""
                <div class="gem-msg">
                    <div class="gem-msg-icon user">U</div>
                    <div class="gem-msg-body">
                        <div class="gem-msg-name">You</div>
                        <div class="gem-msg-text">{content}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="gem-msg">
                    <div class="gem-msg-icon agent">✦</div>
                    <div class="gem-msg-body">
                        <div class="gem-msg-name">Anzum AI</div>
                        <div class="gem-msg-text">{content}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Input card ──
    st.markdown('<div class="gem-input-card">', unsafe_allow_html=True)
    user_input = st.chat_input("Ask me anything…", key="chat_input")
    st.markdown("</div>", unsafe_allow_html=True)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.markdown(
            f"""
            <div class="gem-msg">
                <div class="gem-msg-icon user">U</div>
                <div class="gem-msg-body">
                    <div class="gem-msg-name">You</div>
                    <div class="gem-msg-text">{user_input}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Agent column layout for streaming
        with st.container():
            st.markdown(
                """
                <div class="gem-msg">
                    <div class="gem-msg-icon agent">✦</div>
                    <div class="gem-msg-body">
                        <div class="gem-msg-name">Anzum AI</div>
                """,
                unsafe_allow_html=True,
            )

            # Try FAQ fast-path first
            faq_ans = faq_match(user_input)
            if faq_ans:
                time.sleep(0.3)
                st.markdown(
                    f'<div class="gem-msg-text">{faq_ans}</div>',
                    unsafe_allow_html=True,
                )
                reply = faq_ans
            else:
                reply = stream_response(
                    [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                )

            st.markdown("</div></div>", unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # Clear button
    if st.session_state.messages:
        if st.button("Clear conversation", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ── ABOUT TAB ─────────────────────────────────────────────────────────────────

def render_about_tab():
    st.markdown(
        """
        <div class="gem-hero">
            <div class="gem-avatar">A</div>
            <h1 class="gem-hero-title">About Me</h1>
            <p class="gem-hero-sub">
                Builder, tinkerer, and AI enthusiast. I turn messy ideas into clean,
                working software — with an emphasis on the AI-native approach.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Stats
    st.markdown(
        """
        <div class="gem-stats">
            <div class="gem-stat"><div class="gem-stat-num">4+</div><div class="gem-stat-label">Years</div></div>
            <div class="gem-stat"><div class="gem-stat-num">20+</div><div class="gem-stat-label">Projects</div></div>
            <div class="gem-stat"><div class="gem-stat-num">10k+</div><div class="gem-stat-label">Users</div></div>
            <div class="gem-stat"><div class="gem-stat-num">∞</div><div class="gem-stat-label">Coffee</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # FAQ
    for category, items in FAQ_DATA.items():
        st.markdown(f'<div class="gem-section-title">{category}</div>', unsafe_allow_html=True)
        st.markdown('<div class="gem-faq-grid">', unsafe_allow_html=True)
        for item in items:
            st.markdown(
                f"""
                <div class="gem-faq-card">
                    <div class="gem-faq-q">
                        <div class="gem-faq-icon">?</div>
                        {item['q']}
                    </div>
                    <div class="gem-faq-a">{item['a']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# ── PROJECTS TAB ──────────────────────────────────────────────────────────────

def render_projects_tab():
    st.markdown(
        """
        <div class="gem-hero">
            <h1 class="gem-hero-title">Projects</h1>
            <p class="gem-hero-sub">
                Things I've built — from side experiments to production tools.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="gem-section-title">Featured Work</div>', unsafe_allow_html=True)
    st.markdown('<div class="gem-project-grid">', unsafe_allow_html=True)
    for p in PROJECTS:
        tags_html = "".join(f'<span class="gem-tag">{t}</span>' for t in p["tags"])
        st.markdown(
            f"""
            <div class="gem-project-card">
                <span class="gem-project-icon" style="color:{p['color']}">{p['icon']}</span>
                <div class="gem-project-name">{p['name']}</div>
                <div class="gem-project-desc">{p['desc']}</div>
                <div class="gem-tags">{tags_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ── SKILLS TAB ────────────────────────────────────────────────────────────────

def render_skills_tab():
    st.markdown(
        """
        <div class="gem-hero">
            <h1 class="gem-hero-title">Skills</h1>
            <p class="gem-hero-sub">Technologies and tools I work with daily.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="gem-section-title">Tech Stack</div>', unsafe_allow_html=True)
    st.markdown('<div class="gem-skills-grid">', unsafe_allow_html=True)
    for group, techs in SKILLS_DATA.items():
        badges_html = "".join(f'<span class="gem-skill-badge">{t}</span>' for t in techs)
        st.markdown(
            f"""
            <div class="gem-skill-group">
                <div class="gem-skill-group-title">{group}</div>
                <div>{badges_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ── CONTACT TAB ───────────────────────────────────────────────────────────────

def render_contact_tab():
    st.markdown(
        """
        <div class="gem-hero">
            <h1 class="gem-hero-title">Get in Touch</h1>
            <p class="gem-hero-sub">
                Have a project in mind or just want to chat? Reach out.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="gem-contact-wrap">', unsafe_allow_html=True)

    if st.session_state.contact_sent:
        st.markdown(
            '<div class="gem-alert">✓ Message received! I\'ll get back to you within 24 hours.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Send another message"):
            st.session_state.contact_sent = False
            st.rerun()
    else:
        with st.form("contact_form"):
            st.markdown(
                '<div class="gem-input-card">',
                unsafe_allow_html=True,
            )
            name = st.text_input("", placeholder="Your name", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                '<div class="gem-input-card" style="margin-top:12px">',
                unsafe_allow_html=True,
            )
            email = st.text_input("", placeholder="your@email.com", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                '<div class="gem-input-card" style="margin-top:12px">',
                unsafe_allow_html=True,
            )
            message = st.text_area("", placeholder="What's on your mind?", height=130, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            submitted = st.form_submit_button("Send Message →", use_container_width=True)

            if submitted:
                if name and email and message:
                    # In production: send email / save to DB
                    st.session_state.contact_sent = True
                    st.rerun()
                else:
                    st.warning("Please fill in all fields.")

    st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_session()

    # Inject global CSS
    st.markdown(GEMINI_CSS, unsafe_allow_html=True)

    # ── Tabs via st.tabs (provides Streamlit routing + Gemini-styled) ──
    tab_labels = ["✦ Chat", "👤 About", "🗂 Projects", "⚡ Skills", "✉ Contact"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        render_chat_tab()

    with tabs[1]:
        render_about_tab()

    with tabs[2]:
        render_projects_tab()

    with tabs[3]:
        render_skills_tab()

    with tabs[4]:
        render_contact_tab()

    # Footer
    st.markdown(
        f"""
        <div class="gem-footer">
            Built with ✦ Streamlit &amp; Claude &nbsp;·&nbsp;
            <a href="#">GitHub</a> &nbsp;·&nbsp;
            <a href="#">Twitter</a> &nbsp;·&nbsp;
            © {datetime.now().year} Anzum
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
