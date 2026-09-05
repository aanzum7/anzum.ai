# ──────────────────────────────────────────────────────────────────────────────
# file: ui/styles.py
# ──────────────────────────────────────────────────────────────────────────────
"""
Global Design System and CSS Tokens for anzum.ai
Implements rich glassmorphism, responsive micro-animations, and modern typography.
"""

GLOBAL_CSS = """
<style>
/* ─── Google Fonts Import ─── */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ─── CSS Variables & Design Tokens ─── */
:root {
    --font-heading: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-body: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;

    --bg-primary: #0A0E17;
    --bg-secondary: #131C2E;
    --bg-card: rgba(19, 28, 46, 0.75);
    --bg-card-hover: rgba(30, 41, 59, 0.85);

    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-accent: rgba(99, 102, 241, 0.35);
    --border-glow: rgba(99, 102, 241, 0.6);

    --accent-primary: #6366F1;
    --accent-secondary: #8B5CF6;
    --accent-cyan: #06B6D4;
    --accent-emerald: #10B981;

    --text-main: #F8FAFC;
    --text-muted: #94A3B8;
    --text-dim: #64748B;

    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 8px 24px -4px rgba(0, 0, 0, 0.45);
    --shadow-glow: 0 0 25px -5px rgba(99, 102, 241, 0.35);
}

/* ─── Global Font & Background Overrides ─── */
html, body, [class*="css"] {
    font-family: var(--font-body);
    color: var(--text-main);
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-heading) !important;
    letter-spacing: -0.02em;
}

/* Subtle background radial glow & header transparency */
header[data-testid="stHeader"] {
    background: transparent !important;
}

.stApp {
    background: radial-gradient(circle at 80% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 10% 80%, rgba(6, 182, 212, 0.05) 0%, transparent 40%),
                #0A0E17 !important;
}

/* ─── Hero Header Banner ─── */
.hero-container {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
}

.hero-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366F1, #8B5CF6, #06B6D4, transparent);
}

.hero-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
}

.hero-title {
    font-family: var(--font-heading);
    font-size: 2.3rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 50%, #94A3B8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: flex;
    align-items: center;
    gap: 12px;
}

.hero-title .brand-gradient {
    background: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #A5B4FC;
    letter-spacing: 0.02em;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: pulse-ring 1.8s infinite;
}

@keyframes pulse-ring {
    0% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

.hero-desc {
    font-size: 1.05rem;
    color: var(--text-muted);
    margin-top: 10px;
    margin-bottom: 0;
    line-height: 1.6;
    max-width: 850px;
}

/* ─── Modern Tabs Overhaul ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(19, 28, 46, 0.6) !important;
    backdrop-filter: blur(12px);
    padding: 6px;
    border-radius: 14px;
    border: 1px solid var(--border-subtle);
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    padding: 8px 18px !important;
    font-family: var(--font-heading) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: var(--text-muted) !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-main) !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--border-accent) !important;
    box-shadow: 0 2px 10px rgba(99, 102, 241, 0.2) !important;
}

/* ─── Nested Interactive Subtabs Refinement ─── */
.stTabs .stTabs [data-baseweb="tab-list"] {
    background-color: rgba(15, 23, 42, 0.55) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    margin-bottom: 16px;
    padding: 4px;
    border-radius: 12px;
}

.stTabs .stTabs [data-baseweb="tab"] {
    font-size: 0.88rem !important;
    padding: 6px 14px !important;
    border-radius: 8px !important;
}

.stTabs .stTabs [aria-selected="true"] {
    background: rgba(99, 102, 241, 0.2) !important;
    border-color: rgba(99, 102, 241, 0.35) !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15) !important;
}

/* ─── FAQ Tab Card & Contact Links ─── */
.faq-tab-card {
    background: rgba(19, 28, 46, 0.55);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-subtle);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
}
.faq-tab-card:hover {
    border-color: var(--border-accent);
    background: rgba(30, 41, 59, 0.7);
}
.faq-tab-title {
    font-family: var(--font-heading);
    font-size: 1.05rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.faq-tab-desc {
    font-size: 0.92rem;
    color: #CBD5E1;
    line-height: 1.55;
    margin-bottom: 8px;
}
.contact-link-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 8px;
    margin-bottom: 6px;
}
.contact-link-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #A5B4FC !important;
    text-decoration: none !important;
    transition: all 0.15s ease;
}
.contact-link-tag:hover {
    background: rgba(99, 102, 241, 0.25);
    border-color: var(--border-glow);
    color: #FFFFFF !important;
    transform: translateY(-1px);
}

/* ─── Prominent Sidebar Contact Card (Email & Phone) ─── */
.sidebar-contact-card {
    background: rgba(30, 41, 59, 0.45);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 12px;
    margin-top: 10px;
    margin-bottom: 12px;
}

.contact-card-header {
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #A5B4FC;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.contact-item-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    text-decoration: none !important;
    margin-bottom: 6px;
    transition: all 0.2s ease;
}

.contact-item-row:last-child {
    margin-bottom: 0;
}

.contact-item-row:hover {
    border-color: rgba(99, 102, 241, 0.4);
    background: rgba(99, 102, 241, 0.12);
    transform: translateX(2px);
}

.contact-icon {
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 6px;
    background: rgba(99, 102, 241, 0.15);
}

.contact-details {
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.contact-label {
    font-size: 0.68rem;
    color: #94A3B8;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.04em;
}

.contact-val {
    font-size: 0.82rem;
    color: #F1F5F9;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ─── Suggestion / Quick Prompt Chips ─── */
.chip-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 18px;
    margin-top: 8px;
}

.chip-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: flex;
    align-items: center;
    gap: 6px;
    width: 100%;
    margin-bottom: 2px;
}

/* ─── Chat Message Refinements ─── */
.stChatMessage {
    background: rgba(19, 28, 46, 0.5) !important;
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-subtle) !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: var(--shadow-sm);
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.stChatMessage:hover {
    border-color: rgba(255, 255, 255, 0.12) !important;
}

[data-testid="stChatMessageContent"] {
    font-size: 0.98rem;
    line-height: 1.65;
    color: var(--text-main);
}

/* Highlight FAQ Matches */
.faq-match-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #34D399;
    margin-bottom: 8px;
}

/* ─── Sidebar Glass Card Styling ─── */
[data-testid="stSidebar"] {
    background: #0D1322 !important;
    border-right: 1px solid var(--border-subtle) !important;
}

.sidebar-avatar-container {
    text-align: center;
    padding: 10px 0 16px 0;
}

.avatar-wrapper {
    position: relative;
    display: inline-block;
    border-radius: 50%;
    padding: 4px;
    background: linear-gradient(135deg, #6366F1, #EC4899, #06B6D4);
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.35);
}

.avatar-wrapper img {
    border-radius: 50%;
    display: block;
    width: 90px;
    height: 90px;
    object-fit: cover;
    background: #0F172A;
}

.sidebar-name {
    font-family: var(--font-heading);
    font-size: 1.45rem;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 2px;
    background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sidebar-title-caption {
    font-size: 0.85rem;
    color: #94A3B8;
    line-height: 1.4;
    margin-bottom: 12px;
}

.sidebar-status-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #10B981;
}

.sidebar-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
}

.sidebar-card:hover {
    border-color: var(--border-accent);
    background: rgba(255, 255, 255, 0.05);
}

.sidebar-card-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #A5B4FC;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.sidebar-card-body {
    font-size: 0.85rem;
    color: #CBD5E1;
    line-height: 1.5;
}

/* ─── Focused Sidebar Current Status & Micro-Pills ─── */
.sidebar-current-card {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.04) 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 10px;
}

.current-item {
    margin-bottom: 8px;
}
.current-item:last-child {
    margin-bottom: 0;
}

.current-badge {
    display: inline-block;
    padding: 2px 7px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-radius: 4px;
    background: rgba(99, 102, 241, 0.2);
    color: #A5B4FC;
    margin-bottom: 3px;
}

.current-badge.seeking {
    background: rgba(16, 185, 129, 0.18);
    color: #34D399;
}

.current-title {
    font-size: 0.86rem;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.3;
}

.current-sub {
    font-size: 0.75rem;
    color: #94A3B8;
    margin-top: 1px;
}

.sidebar-pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 6px;
    margin-bottom: 12px;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    color: #CBD5E1;
}

/* ─── Social & Professional Link Buttons ─── */
.link-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 10px;
    margin-bottom: 14px;
}

.link-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 8px 10px;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #E2E8F0 !important;
    text-decoration: none !important;
    transition: all 0.2s ease;
}

.link-btn:hover {
    background: rgba(99, 102, 241, 0.2);
    border-color: var(--border-accent);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
}

/* ─── FAQ Expanders Styling ─── */
.streamlit-expanderHeader {
    background-color: rgba(19, 28, 46, 0.5) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    font-family: var(--font-heading) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: #F1F5F9 !important;
    transition: border-color 0.2s ease, background 0.2s ease;
}

.streamlit-expanderHeader:hover {
    border-color: var(--border-accent) !important;
    background-color: rgba(30, 41, 59, 0.7) !important;
}

.streamlit-expanderContent {
    background: rgba(15, 23, 42, 0.4) !important;
    border: 1px solid var(--border-subtle) !important;
    border-top: none !important;
    border-bottom-left-radius: 10px !important;
    border-bottom-right-radius: 10px !important;
    padding: 16px 20px !important;
    color: #CBD5E1 !important;
    line-height: 1.6 !important;
}

/* ─── Search Box Polishing ─── */
.stTextInput > div > div > input {
    border-radius: 10px !important;
    border: 1px solid var(--border-subtle) !important;
    background: rgba(19, 28, 46, 0.7) !important;
    color: #F8FAFC !important;
    padding: 10px 14px !important;
    font-family: var(--font-body) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.25) !important;
}

/* ─── Chat Input Styling ─── */
[data-testid="stChatInput"] {
    border-radius: 14px !important;
    border: 1px solid var(--border-accent) !important;
    background: rgba(19, 28, 46, 0.85) !important;
    backdrop-filter: blur(16px);
    box-shadow: var(--shadow-md), 0 0 15px rgba(99, 102, 241, 0.15) !important;
    transition: all 0.2s ease;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent-primary) !important;
    box-shadow: var(--shadow-md), 0 0 20px rgba(99, 102, 241, 0.3) !important;
}

/* ─── Buttons Polishing ─── */
.stButton > button {
    border-radius: 10px !important;
    font-family: var(--font-heading) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
}

/* ─── Scrollbars ─── */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.12);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.24);
}
</style>
"""

def inject_styles():
    """Injects the global CSS design system into the Streamlit app."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
