# ──────────────────────────────────────────────────────────────────────────────
# file: app.py (Unified Gemini-Styled Portfolio Agent)
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import os
import sys
import logging
from typing import Dict, List, Tuple, Any, Optional
from difflib import SequenceMatcher

import toml
import streamlit as st
import google.generativeai as genai

# ──────────────────────────────────────────────────────────────────────────────
# 1. LOGGING & INITIALIZATION SETUP
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("anzum_ai")

class ConfigError(Exception):
    """Raised when configuration cannot be loaded or is invalid."""

# ──────────────────────────────────────────────────────────────────────────────
# 2. DATA FALLBACKS & CONFIGURATION HANDLERS
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_MOCK_DATA = {
    "genai": {"api_key": os.getenv("GEMINI_API_KEY", "MOCK_KEY_IF_SECRETS_MISSING")},
    "personal": {
        "data": {
            "name": "Tanvir Anzum",
            "role": "Data Analyst & AI Workflow Engineer",
            "location": "Dhaka, Bangladesh",
            "bio": "Specialized in Python, SQL (BigQuery), automation with Selenium, and building Gemini API agent architectures.",
        }
    },
    "faq": {
        "questions": [
            {
                "category": "Experience",
                "question": "What is Tanvir's primary background?",
                "answer": "Tanvir is a Data Analyst who develops automated ETL pipelines, processes election data systems, and builds Gemini API integrations."
            },
            {
                "category": "Skills",
                "question": "What technologies does he specialize in?",
                "answer": "He actively works with Python, Streamlit, SQL (BigQuery, MySQL), Selenium, and Google Cloud Platform (GCP) ecosystems."
            }
        ]
    }
}

def load_configuration() -> Tuple[List[Dict[str, Any]], Dict[str, Any], str]:
    """Loads configuration safely from secrets or handles sandbox fallbacks."""
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        logger.warning("Secrets file not detected. Booting with sandbox assets.")
        s = DEFAULT_MOCK_DATA
        return s["faq"]["questions"], s["personal"]["data"], s["genai"]["api_key"]

    try:
        secrets = toml.load(secrets_path)
        return secrets["faq"]["questions"], secrets["personal"]["data"], secrets["genai"]["api_key"]
    except Exception as e:
        logger.error(f"Failed to read standard secrets configuration block: {e}")
        s = DEFAULT_MOCK_DATA
        return s["faq"]["questions"], s["personal"]["data"], s["genai"]["api_key"]

# ──────────────────────────────────────────────────────────────────────────────
# 3. DETERMINISTIC FAQ MATCHER & AGENT ENGINE
# ──────────────────────────────────────────────────────────────────────────────
class FAQHandler:
    """Finds the most structurally similar FAQ entry to ground user inputs."""
    def __init__(self, faq_list: List[Dict[str, Any]]):
        self.faq_list = faq_list

    def find_similar_question(self, user_input: str, threshold: float = 0.65) -> Tuple[Optional[str], Optional[str]]:
        most_similar_question, best_answer = None, None
        highest_similarity = 0.0

        target = user_input.lower().strip()
        for faq in self.faq_list:
            q = str(faq.get("question", "")).lower()
            sim = SequenceMatcher(None, target, q).ratio()
            if sim > highest_similarity:
                highest_similarity = sim
                most_similar_question = faq.get("question")
                best_answer = faq.get("answer")

        if highest_similarity >= threshold:
            return most_similar_question, best_answer
        return None, None


class AgenticAI:
    """Resilient interface wrapping Gemini inference with localized safety structures."""
    def __init__(self, api_key: str, context: Dict[str, Any]):
        self.api_key = api_key
        self.context = context
        self.model = None
        self._configure_ai()

    def _configure_ai(self):
        if not self.api_key or self.api_key == "MOCK_KEY_IF_SECRETS_MISSING":
            return
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                generation_config={
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "max_output_tokens": 512,
                },
            )
        except Exception as e:
            logger.exception("Failed to connect with live Generative model cluster.")

    def _build_prompt(self, user_input: str) -> str:
        return (
            f"Based on Tanvir Anzum's profile and expertise context, answer the question accurately.\n\n"
            f"FAQ Grounding Information:\n{self.context.get('faq')}\n\n"
            f"Personal Context Profile:\n{self.context.get('personal')}\n\n"
            f"User Query:\n{user_input}\n\n"
            "Instructions for Response Execution:\n"
            "- Respond strictly as a professional, direct digital representative of Tanvir Anzum.\n"
            "- Keep answers clean, beautifully structured, conversationally fluid, and concise.\n"
            "- Always retain the requested format requested by the user."
        )

    def generate_response(self, user_input: str) -> str:
        if not self.model:
            return "🤖 Hello! I am running in local sandbox mode. Please inject your real `GEMINI_API_KEY` into your secrets file to establish an external inference sync."
        try:
            compiled_prompt = self._build_prompt(user_input)
            response = self.model.generate_content(compiled_prompt)
            if response and response.text:
                return response.text.strip()
            return "🤖 I apologized, I encountered an empty sequence token loop. Please try again."
        except Exception as e:
            logger.exception("Error executing upstream chat loop inference.")
            return f"⚠️ Engine Interface Error: {e}"

# ──────────────────────────────────────────────────────────────────────────────
# 4. INTERFACE COMPONENT FALLBACKS
# ──────────────────────────────────────────────────────────────────────────────
def render_faq_tabs(faq_data: List[Dict[str, Any]]):
    categories = list(set([item.get("category", "General") for item in faq_data]))
    tabs = st.tabs(categories)
    for tab, cat in zip(tabs, categories):
        with tab:
            for item in faq_data:
                if item.get("category") == cat:
                    with st.expander(item.get("question", "")):
                        st.write(item.get("answer", ""))

# ──────────────────────────────────────────────────────────────────────────────
# 5. HIGHLY OPTIMIZED INTERACTIVE CHAT SURFACE
# ──────────────────────────────────────────────────────────────────────────────
def handle_chat_session(faq_handler: FAQHandler, agent: AgenticAI):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display clean historic messaging loops
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Core message evaluation capture
    if user_prompt := st.chat_input("Ask me about Tanvir's skills, projects, or background..."):
        # Append and render user statement instantly
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Trigger inference execution frame
        with st.chat_message("assistant"):
            with st.spinner("Processing intent tokens..."):
                # Track matching ground truth rules before invoking structural LLM processing
                matched_q, matched_a = faq_handler.find_similar_question(user_prompt)
                
                if matched_a:
                    response_text = matched_a
                else:
                    response_text = agent.generate_response(user_prompt)
                
                st.markdown(response_text)
        
        st.session_state.messages.append({"role": "assistant", "content": response_text})

# ──────────────────────────────────────────────────────────────────────────────
# 6. APPLICATION STYLE SHEETS & STRUCTURE MARKS
# ──────────────────────────────────────────────────────────────────────────────
GEMINI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:ital,wght=0,400;0,500;0,600;1,400&family=Google+Sans+Mono:wght=400;500&display=swap');

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

/* ── CRITICAL: SIDEBAR REMOVAL OVERRIDES ── */
[data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], 
section[data-testid="stSidebar"] {
    display: none !important;
    width: 0px !important;
    visibility: hidden !important;
}
.st-emotion-cache-18ni7ap, .st-emotion-cache-79elbk {
    margin-left: 0px !important;
}

/* ── Hide Chrome Layouts ── */
#MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], .stDeployButton { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.09); border-radius: 4px; }

/* ── Hero Presentation Element Structure ── */
.gem-hero {
    padding: 56px 0 44px;
    text-align: center;
    position: relative;
}
.gem-hero::before {
    content: '';
    position: absolute; top: 0; left: 50%;
    transform: translateX(-50%);
    width: 520px; height: 300px;
    background: radial-gradient(ellipse at center, rgba(137,180,248,0.07) 0%, rgba(196,132,252,0.04) 45%, transparent 70%);
    pointer-events: none;
}

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

.gem-thinking-badge {
    display: inline-flex; align-items: center; gap: 9px;
    background: rgba(137,180,248,0.07);
    border: 1px solid rgba(137,180,248,0.18);
    border-radius: 24px;
    padding: 6px 16px;
    margin-bottom: 20px;
    font-size: 12.5px; font-weight: 500; color: var(--blue);
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

.gem-caps {
    display: flex; flex-wrap: wrap; gap: 9px;
    justify-content: center; margin: 28px auto 0; max-width: 620px;
}
.gem-cap {
    display: inline-flex; align-items: center; gap: 7px;
    background: var(--bg2); border: 1px solid var(--line2);
    border-radius: 24px; padding: 7px 15px;
    font-size: 12.5px; font-weight: 500; color: var(--muted);
}
.gem-cap-dot { width: 6px; height: 6px; border-radius: 50%; }

.gem-label {
    display: flex; align-items: center; gap: 10px;
    margin: 44px 0 20px; padding-bottom: 14px;
    border-bottom: 1px solid var(--line);
}
.gem-label-icon {
    width: 32px; height: 32px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; background: var(--bg3);
    border: 1px solid var(--line2); flex-shrink: 0;
}
.gem-label-text {
    font-size: 14px; font-weight: 600; color: var(--muted);
    text-transform: uppercase; letter-spacing: 1px;
}

/* ── Tab Controls ── */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--line) !important; padding: 0 !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--muted) !important; font-size: 13px !important; border-bottom: 2px solid transparent !important; padding: 11px 16px !important; }
.stTabs [aria-selected="true"] { color: var(--blue) !important; border-bottom-color: var(--blue) !important; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding: 16px 0 0 !important; }

details, [data-testid="stExpander"] { background: var(--bg2) !important; border: 1px solid var(--line) !important; border-radius: var(--r) !important; margin-bottom: 10px !important; overflow: hidden; }
details summary, [data-testid="stExpander"] summary { font-size: 14px !important; font-weight: 500 !important; color: var(--text) !important; padding: 15px 18px !important; }
[data-testid="stExpander"] > div > div { padding: 2px 18px 16px !important; color: #9e9e9e !important; font-size: 13.5px !important; line-height: 1.72 !important; }

hr, [data-testid="stDivider"] { border-color: var(--line) !important; margin: 40px 0 !important; }

/* ── Input Layer ── */
[data-testid="stChatInput"] { background: var(--bg2) !important; border: 1px solid var(--line2) !important; border-radius: var(--r2) !important; padding: 6px 10px !important; box-shadow: 0 2px 18px rgba(0,0,0,0.35) !important; }
[data-testid="stChatInput"] textarea { background: transparent !important; color: var(--text) !important; font-size: 15px !important; border: none !important; }
[data-testid="stChatInput"] button { background: var(--grad2) !important; border-radius: 10px !important; }

/* ── Chat Messages ── */
[data-testid="stChatMessage"] { background: transparent !important; border: none !important; padding: 4px 0 !important; gap: 14px !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { background: var(--bg2) !important; border-radius: var(--r2) !important; padding: 16px 20px !important; border: 1px solid var(--line) !important; margin-bottom: 12px; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) { background: transparent !important; border-left: 2px solid rgba(137,180,248,0.25) !important; padding-left: 20px !important; border-radius: 0 !important; margin-bottom: 12px; }

.stButton > button { background: var(--bg3) !important; color: var(--muted) !important; border: 1px solid var(--line2) !important; border-radius: 24px !important; padding: 7px 20px !important; }
.stMarkdown p, .stMarkdown li { color: var(--text) !important; font-size: 14.5px !important; line-height: 1.75 !important; }
.stMarkdown a  { color: var(--blue) !important; text-decoration: none !important; }
.stMarkdown code { background: rgba(255,255,255,0.06) !important; color: #93c5fd !important; border-radius: 5px !important; padding: 1px 6px !important; }

h3 { display: none !important; }
</style>
"""

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
    <p class="gem-tagline" style="max-width: 680px;">Driven by Data, Inspired by Impact | AI & Analytics | Recommendation Models | Turning Insights into Action</p>
    <div class="gem-caps">
        <div class="gem-cap"><div class="gem-cap-dot" style="background:#89b4f8"></div>Data Analysis</div>
        <div class="gem-cap"><div class="gem-cap-dot" style="background:#c084fc"></div>ETL Pipelines</div>
        <div class="gem-cap"><div class="gem-cap-dot" style="background:#4ade80"></div>Election Scraping</div>
        <div class="gem-cap"><div class="gem-cap-dot" style="background:#f472b6"></div>Gemini API</div>
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
# 7. RUNTIME APP EXECUTION ENTRYPOINT
# ──────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="anzum.ai",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Render CSS and premium header modules
    st.markdown(GEMINI_CSS, unsafe_allow_html=True)
    st.markdown(HERO_HTML, unsafe_allow_html=True)

    # Initialize assets and handlers
    faq_data, personal_context, api_key = load_configuration()
    faq_handler = FAQHandler(faq_data)
    agent = AgenticAI(api_key=api_key, context={"faq": faq_data, "personal": personal_context})

    # FAQ Section
    st.markdown(FAQ_LABEL, unsafe_allow_html=True)
    try:
        from ui.faq_view import render_faq_tabs as actual_faq_tabs
        actual_faq_tabs(faq_data)
    except ImportError:
        render_faq_tabs(faq_data)

    st.divider()

    # Chat Module Section
    st.markdown(CHAT_LABEL, unsafe_allow_html=True)
    handle_chat_session(faq_handler=faq_handler, agent=agent)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application crashed: {e}")
        logger.exception("Fatal runtime event generated execution fault.")
