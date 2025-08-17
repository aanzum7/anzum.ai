# ──────────────────────────────────────────────────────────────────────────────
# file: services/config.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Dict, List, Tuple
import toml
import os

class ConfigError(Exception):
    """Raised when configuration cannot be loaded or is invalid."""

def _validate_config(secrets: Dict) -> Tuple[List[Dict], Dict, str]:
    try:
        faq_data = secrets["faq"]["questions"]
        personal_context = secrets["personal"]["data"]
        api_key = secrets["genai"]["api_key"]
    except Exception as e:
        raise ConfigError(f"Missing or malformed keys in secrets.toml: {e}")

    if not isinstance(faq_data, list) or not all(isinstance(x, dict) for x in faq_data):
        raise ConfigError("faq.questions must be a list of dicts.")
    if not isinstance(personal_context, dict):
        raise ConfigError("personal.data must be a dict.")
    if not api_key or not isinstance(api_key, str):
        raise ConfigError("genai.api_key must be a non-empty string.")

    return faq_data, personal_context, api_key

def load_configuration() -> Tuple[List[Dict], Dict, str]:
    """
    Load configuration from .streamlit/secrets.toml and validate.
    Returns (faq_data, personal_context, api_key).
    """
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        raise ConfigError(
            "`.streamlit/secrets.toml` not found. Please create it using the schema below:\n\n"
            "[genai]\napi_key = \"YOUR_GEMINI_API_KEY\"\n\n"
            "[personal]\n  [personal.data]\n  name = \"Tanvir Anzum\"\n  # ... other fields\n\n"
            "[faq]\n  questions = [\n    { category = \"Experience\", question = \"...\", answer = \"...\" },\n  ]"
        )

    try:
        secrets = toml.load(secrets_path)
    except Exception as e:
        raise ConfigError(f"Failed to parse secrets.toml: {e}")

    return _validate_config(secrets)

