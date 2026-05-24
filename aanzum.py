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
# GEMINI AGENTIC CSS
# ──────────────────────────────────────────────────────────────────────────────

GEMINI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:ital,wght@0,400;0,500;0,600;1,400&family=Google+Sans+Mono:wght@400;500&display=swap');

:root {
    --bg:        #131314;
    --bg2:       #1e1f20;
    --bg3:       #28292a;
    --line:      rgba(255,255,255,0.07);
    --line2:     rgba(255,255,255,0.13);
    --text:      #e3e3e3;
    --muted:     #8e918f;
    --blue:      #89b4f8;
    --purple:    #c084fc;
    --teal:      #4ade80;
    --grad:      linear-gradient(90deg,#89b4f8,#c084fc,#f472b6);
    --grad2:     linear-gradient(135deg,#89b4f8 0%,#c084fc 60%,#f472b6 100%);
    --r:         14px;
    --r2:        20px;
    --font:      'Google Sans', sans-serif;
    --mono:      'Google Sans Mono', monospace;
}

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="st-"] { font-family: var(--font) !important; }
.stApp { background: var(--bg) !important; }
.block-container {
    max-width: 860px !important;
    padding: 0 2rem 6rem !important;
    margin: 0 auto !important;
}

/* ── Hide chrome ── */
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], .stDeployButton { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.09); border-radius: 4px; }

/* ────────────────────────────────────────────────────
   SIDEBAR — clean dark panel
   ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] > div { padding-top: 1.5rem !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--text) !important; }
[data-testid="stSidebar"] a   { color: var(--blue) !important; }
[data-testid="stSidebar"] strong { color: var(--text) !important; }
[data-testid="stSidebar"] .stMarkdown p { font-size: 13.5px !important; line-height: 1.65 !important; color: #aaa !important; }
[data-testid="stSidebar"] h3  { font-size: 15px !important; font-weight: 600 !important; color: var(--text) !important; }

/* ────────────────────────────────────────────────────
   HERO
   ──────────────────────────────────────────────────── */
.gem-hero {
    padding: 56px 0 44px;
    text-align: center;
    position: relative;
}
/* subtle background glow */
.gem-hero::before {
    content: '';
    position: absolute; top: 0; left: 50%;
    transform: translateX(-50%);
    width: 520px; height: 300px;
    background: radial-gradient(ellipse at center,
        rgba(137,180,248,0.07) 0%,
        rgba(196,132,252,0.04) 45%,
        transparent 70%);
    pointer-events: none;
}

/* Avatar with animated ring */
.gem-avatar-wrap {
    position: relative;
    width: 72px; height: 72px;
    margin: 0 auto 18px;
}
.gem-avatar {
    width: 72px; height: 72px;
    border-radius: 50%;
    background: var(--grad2);
    display: flex; align-items: center; justify-content: center;
    font-size: 26px; font-weight: 600; color: #fff;
    position: relative; z-index: 1;
}
.gem-avatar-ring {
    position: absolute; inset: -4px;
    border-radius: 50%;
    background: conic-gradient(from 0deg, #89b4f8, #c084fc, #f472b6, #89b4f8);
    animation: spin 4s linear infinite;
    z-index: 0;
}
.gem-avatar-ring::after {
    content: '';
    position: absolute; inset: 3px;
    border-radius: 50%;
    background: var(--bg);
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Thinking badge */
.gem-thinking-badge {
    display: inline-flex; align-items: center; gap: 9px;
    background: rgba(137,180,248,0.07);
    border: 1px solid rgba(137,180,248,0.18);
    border-radius: 24px;
    padding: 6px 16px;
    margin-bottom: 20px;
    font-size: 12.5px; font-weight: 500; color: var(--blue);
    letter-spacing: 0.2px;
}
.gem-thinking-dots { display: flex; gap: 4px; align-items: center; }
.gem-thinking-dots span {
    width: 5px; height: 5px; border-radius: 50%;
    background: var(--blue);
    animation: tdot 1.4s ease-in-out infinite;
}
.gem-thinking-dots span:nth-child(2) { animation-delay: .2s; background: var(--purple); }
.gem-thinking-dots span:nth-child(3) { animation-delay: .4s; background: #f472b6; }
@keyframes tdot {
    0%,80%,100% { transform: scale(.6); opacity:.35; }
    40%         { transform: scale(1); opacity:1; }
}

.gem-name {
    font-size: 42px; font-weight: 600; letter-spacing: -1px;
    background: var(--grad);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 10px;
    line-height: 1.1;
}
.gem-tagline {
    font-size: 15.5px; color: var(--muted);
    max-width: 420px; margin: 0 auto;
    line-height: 1.65;
}

/* ────────────────────────────────────────────────────
   AGENT CAPABILITY CHIPS  (below hero)
   ──────────────────────────────────────────────────── */
.gem-caps {
    display: flex; flex-wrap: wrap; gap: 9px;
    justify-content: center;
    margin: 28px auto 0;
    max-width: 620px;
}
.gem-cap {
    display: inline-flex; align-items: center; gap: 7px;
    background: var(--bg2);
    border: 1px solid var(--line2);
    border-radius: 24px;
    padding: 7px 15px;
    font-size: 12.5px; font-weight: 500; color: var(--muted);
    transition: all .2s;
}
.gem-cap:hover {
    border-color: rgba(137,180,248,0.35);
    color: var(--blue);
    background: rgba(137,180,248,0.06);
}
.gem-cap-dot {
    width: 6px; height: 6px; border-radius: 50%;
}

/* ────────────────────────────────────────────────────
   SECTION LABEL  (replaces st.subheader)
   ──────────────────────────────────────────────────── */
.gem-label {
    display: flex; align-items: center; gap: 10px;
    margin: 44px 0 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--line);
}
.gem-label-icon {
    width: 32px; height: 32px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    background: var(--bg3);
    border: 1px solid var(--line2);
    flex-shrink: 0;
}
.gem-label-text {
    font-size: 14px; font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ────────────────────────────────────────────────────
   FAQ  tabs + expanders
   ──────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--line) !important;
    gap: 0 !important; padding: 0 !important;
    margin-bottom: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: var(--font) !important;
    font-size: 13px !important; font-weight: 500 !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 11px 16px !important;
    border-radius: 0 !important;
    transition: color .15s !important;
}
.stTabs [aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom-color: var(--blue) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 16px 0 0 !important;
}

details, [data-testid="stExpander"] {
    background: var(--bg2) !important;
    border: 1px solid var(--line) !important;
    border-radius: var(--r) !important;
    margin-bottom: 10px !important;
    overflow: hidden;
    transition: border-color .2s, background .2s;
}
details:hover, [data-testid="stExpander"]:hover {
    background: var(--bg3) !important;
    border-color: var(--line2) !important;
}
details[open], [data-testid="stExpander"][open] {
    border-color: rgba(137,180,248,0.28) !important;
    background: var(--bg2) !important;
}
details summary,
[data-testid="stExpander"] summary {
    font-size: 14px !important; font-weight: 500 !important;
    color: var(--text) !important;
    padding: 15px 18px !important;
    cursor: pointer; list-style: none;
}
[data-testid="stExpander"] > div > div {
    padding: 2px 18px 16px !important;
    color: #9e9e9e !important;
    font-size: 13.5px !important;
    line-height: 1.72 !important;
}

/* ────────────────────────────────────────────────────
   DIVIDER
   ──────────────────────────────────────────────────── */
hr, [data-testid="stDivider"] {
    border-color: var(--line) !important;
    margin: 40px 0 !important;
}

/* ────────────────────────────────────────────────────
   CHAT INPUT  — Gemini bottom bar style
   ──────────────────────────────────────────────────── */
[data-testid="stChatInput"] {
    background: var(--bg2) !important;
    border: 1px solid var(--line2) !important;
    border-radius: var(--r2) !important;
    padding: 6px 10px !important;
    transition: border-color .2s, box-shadow .2s;
    box-shadow: 0 2px 18px rgba(0,0,0,0.35) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(137,180,248,0.45) !important;
    box-shadow: 0 0 0 3px rgba(137,180,248,0.08), 0 2px 18px rgba(0,0,0,0.35) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 15px !important;
    border: none !important; box-shadow: none !important;
    caret-color: var(--blue) !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #555 !important; }

/* send button */
[data-testid="stChatInput"] button {
    background: var(--grad2) !important;
    border: none !important;
    border-radius: 10px !important;
    width: 36px !important; height: 36px !important;
    color: #fff !important;
}

/* ────────────────────────────────────────────────────
   CHAT MESSAGES
   ──────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 4px 0 !important;
    gap: 14px !important;
}

/* user turn */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--bg2) !important;
    border-radius: var(--r2) !important;
    padding: 16px 20px !important;
    margin-bottom: 6px !important;
    border: 1px solid var(--line) !important;
}

/* assistant turn */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: transparent !important;
    border: none !important;
    padding: 16px 4px !important;
    margin-bottom: 6px !important;
    border-left: 2px solid rgba(137,180,248,0.25) !important;
    padding-left: 20px !important;
    border-radius: 0 !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    color: var(--text) !important;
    font-size: 15px !important; line-height: 1.78 !important;
}
[data-testid="stChatMessage"] strong { color: #fff !important; font-weight: 600 !important; }
[data-testid="stChatMessage"] code {
    background: rgba(255,255,255,0.06) !important;
    color: #93c5fd !important;
    font-family: var(--mono) !important;
    border-radius: 6px !important;
    padding: 2px 7px !important;
    font-size: 13px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stChatMessage"] pre {
    background: var(--bg2) !important;
    border: 1px solid var(--line2) !important;
    border-radius: var(--r) !important;
    padding: 16px !important;
}

/* Avatars */
[data-testid="chatAvatarIcon-user"] {
    background: rgba(137,180,248,0.12) !important;
    color: var(--blue) !important;
    border: 1px solid rgba(137,180,248,0.22) !important;
    border-radius: 50% !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: var(--grad2) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50% !important;
}

/* ────────────────────────────────────────────────────
   BUTTONS
   ──────────────────────────────────────────────────── */
.stButton > button {
    background: var(--bg3) !important;
    color: var(--muted) !important;
    border: 1px solid var(--line2) !important;
    border-radius: 24px !important;
    font-family: var(--font) !important;
    font-size: 13px !important; font-weight: 500 !important;
    padding: 7px 20px !important;
    transition: all .18s !important;
}
.stButton > button:hover {
    background: rgba(137,180,248,0.08) !important;
    border-color: rgba(137,180,248,0.32) !important;
    color: var(--blue) !important;
    transform: translateY(-1px) !important;
}

/* ────────────────────────────────────────────────────
   TEXT INPUTS (sidebar etc.)
   ──────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg3) !important;
    border: 1px solid var(--line2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font) !important; font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(137,180,248,0.4) !important;
    box-shadow: 0 0 0 2px rgba(137,180,248,0.08) !important;
}
label {
    color: var(--muted) !important;
    font-size: 12px !important; font-weight: 500 !important;
    text-transform: uppercase !important; letter-spacing: .7px !important;
}

/* ────────────────────────────────────────────────────
   MARKDOWN
   ──────────────────────────────────────────────────── */
.stMarkdown p, .stMarkdown li { color: var(--text) !important; font-size: 14.5px !important; line-height: 1.75 !important; }
.stMarkdown a  { color: var(--blue) !important; text-decoration: none !important; }
.stMarkdown a:hover { text-decoration: underline !important; }
.stMarkdown strong { color: #fff !important; font-weight: 600 !important; }
.stMarkdown code {
    background: rgba(255,255,255,0.06) !important;
    color: #93c5fd !important;
    font-family: var(--mono) !important;
    border-radius: 5px !important; padding: 1px 6px !important; font-size: 13px !important;
}

/* ────────────────────────────────────────────────────
   ALERTS / ERRORS
   ──────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: rgba(244,75,95,0.06) !important;
    border: 1px solid rgba(244,75,95,0.2) !important;
    border-radius: 12px !important;
    color: #fca5a5 !important;
}

/* suppress all h3 default Streamlit rendering */
h3 { display: none !important; }
</style>
"""

# ──────────────────────────────────────────────────────────────────────────────
# HERO HTML
# ──────────────────────────────────────────────────────────────────────────────

HERO_HTML = """
<div class="gem-hero">
    <div class="gem-avatar-wrap">
        <div class="gem-avatar-ring"></div>
        <div class="gem-avatar">A</div>
    </div>

    <div class="gem-thinking-badge">
        <div class="gem-thinking-dots">
            <span></span><span></span><span></span>
        </div>
        Ready to assist
    </div>

    <h1 class="gem-name">anzum.ai</h1>
    <p class="gem-tagline">
        Ask me anything about Tanvir Anzum —
        research, projects, skills, and experience.
    </p>

    <div class="gem-caps">
        <div class="gem-cap">
            <div class="gem-cap-dot" style="background:#89b4f8"></div>
            Research & Papers
        </div>
        <div class="gem-cap">
            <div class="gem-cap-dot" style="background:#c084fc"></div>
            ML / NLP Projects
        </div>
        <div class="gem-cap">
            <div class="gem-cap-dot" style="background:#4ade80"></div>
            Career Journey
        </div>
        <div class="gem-cap">
            <div class="gem-cap-dot" style="background:#f472b6"></div>
            Consulting & Work
        </div>
        <div class="gem-cap">
            <div class="gem-cap-dot" style="background:#fbbf24"></div>
            Skills & Technologies
        </div>
    </div>
</div>
"""

FAQ_LABEL = """
<div class="gem-label">
    <div class="gem-label-icon">💡</div>
    <span class="gem-label-text">Frequently Asked Questions</span>
</div>
"""

CHAT_LABEL = """
<div class="gem-label">
    <div class="gem-label-icon">✦</div>
    <span class="gem-label-text">Ask anzum.ai</span>
</div>
"""


# ──────────────────────────────────────────────────────────────────────────────
# ORIGINAL BUILD / MAIN
# ──────────────────────────────────────────────────────────────────────────────

def build_app():
    """Create and wire up app dependencies."""
    faq_data, personal_context, api_key = load_configuration()
    faq_handler = FAQHandler(faq_data)
    agent = AgenticAI(api_key=api_key, context={"faq": faq_data, "personal": personal_context})
    return faq_handler, agent, faq_data


def main():
    st.set_page_config(
        page_title="anzum.ai",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(GEMINI_CSS, unsafe_allow_html=True)
    st.markdown(HERO_HTML, unsafe_allow_html=True)

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

    render_sidebar()

    st.markdown(FAQ_LABEL, unsafe_allow_html=True)
    render_faq_tabs(faq_data)

    st.divider()

    st.markdown(CHAT_LABEL, unsafe_allow_html=True)
    render_chat(faq_handler=faq_handler, agent=agent)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.exception("Application crashed.")
