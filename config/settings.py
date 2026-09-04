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
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"
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
    ("🎯 TUHH & Background", "What is your current background and what opportunities are you seeking?"),
    ("🚀 Recommendation Engines", "What did you achieve at Prothom Alo and Brain Station 23?"),
    ("⚡ Tech Stack & Skills", "What are your core technical skills and tools?"),
    ("🎓 Education & Research", "What is your educational background and research publications?"),
    ("🤝 Connect in Hamburg", "How can I connect with Tanvir in Hamburg or globally?"),
]
