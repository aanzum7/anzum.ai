# ──────────────────────────────────────────────────────────────────────────────
# file: config/settings.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_DIR = BASE_DIR / "logo"

# Paths
SECRETS_PATH = BASE_DIR / ".streamlit" / "secrets.toml"
AVATAR_PATH = LOGO_DIR / "aanzum7.png"

# Application Metadata
APP_TITLE = "anzum.ai • Tanvir Anzum's AI Twin"
APP_SUBTITLE = "Data Analytics & Applied AI • Incoming TUHH Master's Student"
APP_VERSION = "2.2.0"
APP_ICON = str(AVATAR_PATH) if AVATAR_PATH.exists() else "🤖"
AUTHOR = "Tanvir Anzum"

# AI Service Defaults (Tuned for short, punchy, high-impact answers)
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

# Comprehensive pool of all Gemini text-to-text models for automatic quota failover
GEMINI_FALLBACK_MODELS: List[str] = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-3.1-pro-preview",
    "gemini-pro-latest",
    "gemini-2.5-pro",
]

# Cooldown duration (seconds) before retrying a model that hit quota limits
MODEL_QUOTA_COOLDOWN_SECONDS = 600

# Rate Limiting & Abuse Prevention (Single chat / device protection)
MIN_REQUEST_INTERVAL_SECONDS = 2.0   # 2-second debounce between rapid queries
MAX_REQUESTS_PER_MINUTE = 6          # Max 6 queries per rolling minute
MAX_SESSION_REQUESTS = 40            # Max 40 queries per session

# Semantic & Similar Asking Cache Settings
CACHE_SIMILARITY_THRESHOLD = 0.65    # Score above which similar query uses cache
CACHE_MAX_ENTRIES = 300              # Maximum LRU cache capacity

GENERATION_CONFIG = {
    "temperature": 0.5,
    "top_p": 0.90,
    "max_output_tokens": 350,
}

# FAQ Engine Settings
FAQ_SIMILARITY_THRESHOLD = 0.60

CATEGORY_ICONS: Dict[str, str] = {
    "Role": "🎓",
    "Experience": "💼",
    "Expertise": "⚡",
    "Education": "🔬",
    "Contact": "🤝",
    "General": "💡"
}

FAQ_CATEGORY_ORDER: List[str] = [
    "Role", "Experience", "Expertise", "Education", "Contact"
]

SUGGESTION_CHIPS: List[Tuple[str, str]] = [
    ("🎯 Background & TUHH", "What is your current background and what opportunities are you seeking?"),
    ("🚀 RecSys & AI Work", "What did you achieve at Prothom Alo and Brain Station 23?"),
    ("⚡ Tech Stack & Tools", "What are your core technical skills and tools?"),
    ("🔬 Research & Papers", "What is your educational background and research publications?"),
    ("🤝 Connect & Hire", "How can I connect with Tanvir in Hamburg or globally?"),
]
