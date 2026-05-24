import streamlit as st
from services.config import load_configuration, ConfigError
from services.logger import get_logger
from services.agentic_ai import AgenticAI
from services.faq import FAQHandler
from ui.sidebar import render_sidebar
from ui.faq_view import render_faq_tabs
from ui.chat import render_chat

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# GEMINI-STYLE CSS  (UI only — zero logic changes)
# ──────────────────────────────────────────────────────────────────────────────

GEMINI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600&family=Google+Sans+Mono&display=swap');

/* ── Tokens ── */
:root {
    --bg:           #0f0f0f;
    --surface:      #1a1a1a;
    --surface-2:    #222222;
    --border:       rgba(255,255,255,0.08);
    --border-hover: rgba(255,255,255,0.16);
    --text:         #e8eaed;
    --muted:        #9aa0a6;
    --accent:       #8ab4f8;
    --accent-p:     #a78bfa;
    --accent-g:     #34d399;
    --grad:         linear-gradient(135deg, #8ab4f8 0%, #a78bfa 50%, #f472b6 100%);
    --r:            16px;
    --r-sm:         10px;
    --font:         'Google Sans', 'Segoe UI', sans-serif;
    --mono:         'Google Sans Mono', monospace;
}

/* ── Reset ── */
html, body, [class*="st-"] { font-family: var(--font) !important; }
.stApp                      { background: var(--bg) !important; }
.block-container            { padding: 2rem 2.5rem 4rem !important; max-width: 1140px !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], .stDeployButton { display: none !important; }

header[data-testid="stHeader"] {
    background: rgba(15,15,15,0.88) !important;
    backdrop-filter: blur(18px) !important;
    border-bottom: 1px solid var(--border) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }

/* ──────────────────────────────────────────────────────
   SIDEBAR
   ────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ──────────────────────────────────────────────────────
   PAGE HEADER  (replaces plain st.subheader)
   ────────────────────────────────────────────────────── */
.gem-page-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 0 0 28px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
}

.gem-page-header-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(138,180,248,0.18), rgba(167,139,250,0.18));
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
}

.gem-page-header-title {
    font-size: 22px;
    font-weight: 600;
    background: var(--grad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.2;
}

.gem-page-header-sub {
    font-size: 13px;
    color: var(--muted);
    margin: 2px 0 0;
}

/* ──────────────────────────────────────────────────────
   HERO STRIP  (top of page)
   ────────────────────────────────────────────────────── */
.gem-hero {
    text-align: center;
    padding: 48px 0 40px;
    position: relative;
}

.gem-hero::before {
    content: '';
    position: absolute;
    top: -60px; left: 50%;
    transform: translateX(-50%);
    width: 560px; height: 360px;
    background: radial-gradient(ellipse, rgba(138,180,248,0.05) 0%, transparent 70%);
    pointer-events: none;
}

.gem-avatar {
    width: 72px; height: 72px;
    margin: 0 auto 20px;
    border-radius: 50%;
    background: var(--grad);
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; color: #fff; font-weight: 600;
    position: relative;
}

.gem-avatar::after {
    content: '';
    position: absolute; inset: -3px;
    border-radius: 50%;
    background: var(--grad);
    z-index: -1; opacity: 0.35;
    filter: blur(8px);
}

.gem-hero-title {
    font-size: 40px; font-weight: 600;
    letter-spacing: -0.8px; line-height: 1.15;
    background: var(--grad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 12px;
}

.gem-hero-sub {
    font-size: 16px; color: var(--muted);
    max-width: 480px; margin: 0 auto 24px;
    line-height: 1.65;
}

.gem-status-pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(52,211,153,0.08);
    border: 1px solid rgba(52,211,153,0.22);
    color: var(--accent-g);
    font-size: 12.5px; font-weight: 500;
    padding: 5px 14px; border-radius: 24px;
}

.gem-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--accent-g);
    animation: blink 2s infinite;
}

@keyframes blink {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.4; transform:scale(1.35); }
}

/* ──────────────────────────────────────────────────────
   FAQ  (wraps render_faq_tabs)
   ────────────────────────────────────────────────────── */

/* Tab bar */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: var(--font) !important;
    font-size: 13.5px !important; font-weight: 500 !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 12px 18px !important;
    border-radius: 0 !important;
    transition: color .18s !important;
}

.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"]     { background: transparent !important; padding: 20px 0 0 !important; }

/* st.expander → FAQ card */
details, [data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    margin-bottom: 12px !important;
    overflow: hidden;
    transition: border-color .2s;
}

details:hover, [data-testid="stExpander"]:hover {
    border-color: var(--border-hover) !important;
}

details summary, [data-testid="stExpander"] summary {
    font-size: 14.5px !important; font-weight: 500 !important;
    color: var(--text) !important;
    padding: 16px 20px !important;
    cursor: pointer;
    list-style: none;
}

details[open], [data-testid="stExpander"][open] {
    border-color: rgba(138,180,248,0.3) !important;
}

/* expander body */
[data-testid="stExpander"] > div > div {
    padding: 0 20px 18px !important;
    color: var(--muted) !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
}

/* ──────────────────────────────────────────────────────
   DIVIDER
   ────────────────────────────────────────────────────── */
hr, [data-testid="stDivider"] {
    border-color: var(--border) !important;
    margin: 36px 0 !important;
}

/* ──────────────────────────────────────────────────────
   CHAT  (wraps render_chat)
   ────────────────────────────────────────────────────── */

/* st.chat_input */
[data-testid="stChatInput"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 4px 8px !important;
    transition: border-color .2s;
}

[data-testid="stChatInput"]:focus-within {
    border-color: rgba(138,180,248,0.4) !important;
    box-shadow: 0 0 0 3px rgba(138,180,248,0.07) !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 15px !important;
    border: none !important;
    box-shadow: none !important;
}

/* st.chat_message bubbles */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 6px 0 !important;
    border: none !important;
}

/* user bubble */
[data-testid="stChatMessage"][data-testid*="user"],
[data-testid="stChatMessage"]:has([aria-label="user avatar"]) {
    background: rgba(138,180,248,0.05) !important;
    border-radius: var(--r) !important;
    padding: 14px 18px !important;
}

/* assistant bubble */
[data-testid="stChatMessage"]:has([aria-label="assistant avatar"]),
[data-testid="stChatMessage"]:has([aria-label="ai avatar"]) {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    padding: 14px 18px !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    color: var(--text) !important;
    font-size: 15px !important;
    line-height: 1.75 !important;
}

[data-testid="stChatMessage"] code {
    background: rgba(255,255,255,0.07) !important;
    color: var(--accent) !important;
    font-family: var(--mono) !important;
    border-radius: 5px !important;
    padding: 1px 6px !important;
    font-size: 13px !important;
}

/* avatar circles */
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
    background: rgba(138,180,248,0.14) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(138,180,248,0.25) !important;
}

[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
    background: var(--grad) !important;
    color: #fff !important;
    border: none !important;
}

/* ──────────────────────────────────────────────────────
   BUTTONS
   ────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--surface-2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 24px !important;
    font-family: var(--font) !important;
    font-size: 13.5px !important; font-weight: 500 !important;
    padding: 8px 22px !important;
    transition: background .18s, border-color .18s, transform .15s !important;
}

.stButton > button:hover {
    background: rgba(138,180,248,0.1) !important;
    border-color: rgba(138,180,248,0.35) !important;
    color: var(--accent) !important;
    transform: translateY(-1px) !important;
}

/* primary / send button */
.stButton > button[kind="primary"] {
    background: var(--grad) !important;
    border: none !important;
    color: #fff !important;
}

/* ──────────────────────────────────────────────────────
   TEXT INPUTS (sidebar, forms, etc.)
   ────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stSelectbox > div > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 14px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
    border-color: rgba(138,180,248,0.4) !important;
    box-shadow: 0 0 0 2px rgba(138,180,248,0.08) !important;
}

label, .stTextInput label, .stTextArea label {
    color: var(--muted) !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
}

/* ──────────────────────────────────────────────────────
   SUBHEADER overrides  (our render_* calls use st.subheader)
   ────────────────────────────────────────────────────── */
h3 {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.9px !important;
    margin: 0 0 20px !important;
}

/* ──────────────────────────────────────────────────────
   ALERTS / ERRORS
   ────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: rgba(244,75,95,0.07) !important;
    border: 1px solid rgba(244,75,95,0.22) !important;
    border-radius: var(--r-sm) !important;
    color: #f87171 !important;
}

/* ──────────────────────────────────────────────────────
   SPINNER / STATUS
   ────────────────────────────────────────────────────── */
[data-testid="stSpinner"] > div {
    border-color: var(--accent) transparent transparent !important;
}

/* ──────────────────────────────────────────────────────
   MARKDOWN body text
   ────────────────────────────────────────────────────── */
.stMarkdown p, .stMarkdown li { color: var(--text) !important; font-size: 15px !important; line-height: 1.75 !important; }
.stMarkdown a { color: var(--accent) !important; text-decoration: none !important; }
.stMarkdown a:hover { text-decoration: underline !important; }
.stMarkdown strong { color: var(--text) !important; font-weight: 600 !important; }
.stMarkdown code { background: rgba(255,255,255,0.07) !important; color: var(--accent) !important;
    font-family: var(--mono) !important; border-radius: 5px !important; padding: 1px 6px !important; font-size: 13px !important; }

</style>
"""


# ──────────────────────────────────────────────────────────────────────────────
# ORIGINAL BUILD / MAIN  (zero changes to logic)
# ──────────────────────────────────────────────────────────────────────────────

def build_app():
    """Create and wire up app dependencies."""
    faq_data, personal_context, api_key = load_configuration()
    faq_handler = FAQHandler(faq_data)
    agent = AgenticAI(
        api_key=api_key,
        context={"faq": faq_data, "personal": personal_context},
    )
    return faq_handler, agent, faq_data


def main():
    st.set_page_config(
        page_title="anzum.ai",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── Inject Gemini CSS ──────────────────────────────────────────────────────
    st.markdown(GEMINI_CSS, unsafe_allow_html=True)

    # ── Hero strip ────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="gem-hero">
            <div class="gem-avatar">A</div>
            <div class="gem-status-pill">
                <div class="gem-dot"></div>
                Available for projects
            </div>
            <h1 class="gem-hero-title">anzum.ai</h1>
            <p class="gem-hero-sub">
                Your personal AI agent — ask me anything about Anzum's work,
                skills, and projects.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Build services (original logic, untouched) ────────────────────────────
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

    # ── Sidebar (original) ────────────────────────────────────────────────────
    render_sidebar()

    # ── FAQ section header ────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="gem-page-header">
            <div class="gem-page-header-icon">💡</div>
            <div>
                <p class="gem-page-header-title">Frequently Asked Questions</p>
                <p class="gem-page-header-sub">Quick answers about Anzum's work and background</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── FAQ tabs (original render_faq_tabs — untouched) ───────────────────────
    render_faq_tabs(faq_data)

    st.divider()

    # ── Chat section header ───────────────────────────────────────────────────
    st.markdown(
        """
        <div class="gem-page-header">
            <div class="gem-page-header-icon">💬</div>
            <div>
                <p class="gem-page-header-title">Chat with anzum.ai</p>
                <p class="gem-page-header-sub">Powered by Claude — ask me anything</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Chat (original render_chat — untouched) ───────────────────────────────
    render_chat(faq_handler=faq_handler, agent=agent)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.exception("Application crashed.")
