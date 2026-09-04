# ──────────────────────────────────────────────────────────────────────────────
# file: services/config.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import os
from typing import Dict, List, Tuple
import streamlit as st
import toml

from config.settings import SECRETS_PATH
from services.logger import get_logger

logger = get_logger(__name__)

class ConfigError(Exception):
    """Raised when configuration, data, or credentials cannot be loaded."""


def _get_secrets_dict() -> Dict:
    """Retrieve full secrets dictionary from st.secrets or local secrets.toml."""
    # 1. Check native st.secrets (Streamlit runtime / Cloud deployment)
    try:
        if hasattr(st, "secrets") and len(st.secrets) > 0:
            return {
                k: dict(v) if hasattr(v, "to_dict") or isinstance(v, dict) else v
                for k, v in st.secrets.items()
            }
    except Exception as e:
        logger.debug(f"Unable to read from st.secrets directly: {e}")

    # 2. Check local secrets.toml
    if os.path.exists(SECRETS_PATH):
        try:
            return toml.load(str(SECRETS_PATH))
        except Exception as e:
            logger.error(f"Failed to parse {SECRETS_PATH}: {e}")

    return {}


@st.cache_data(show_spinner=False)
def load_configuration() -> Tuple[List[Dict], Dict, str]:
    """
    Load credentials, personal context, and FAQs strictly from secrets (zero git exposure).
    Cached across reruns for optimal performance.
    """
    secrets_data = _get_secrets_dict()

    # 1. Resolve API Key
    api_key = None
    if "genai" in secrets_data and "api_key" in secrets_data["genai"]:
        api_key = str(secrets_data["genai"]["api_key"]).strip()
    elif "GEMINI_API_KEY" in secrets_data:
        api_key = str(secrets_data["GEMINI_API_KEY"]).strip()
    else:
        for env_var in ("GEMINI_API_KEY", "GENAI_API_KEY"):
            val = os.environ.get(env_var)
            if val:
                api_key = val.strip()
                break

    if not api_key:
        raise ConfigError(
            "Gemini API Key not found!\n"
            "Please provide it in `.streamlit/secrets.toml` under `[genai] api_key`."
        )

    # 2. Resolve Personal Context (Strictly from secrets for privacy)
    personal_context = {}
    if "personal" in secrets_data and "data" in secrets_data["personal"]:
        personal_context = secrets_data["personal"]["data"]
    elif "personal" in secrets_data and isinstance(secrets_data["personal"], dict):
        personal_context = secrets_data["personal"]

    # 3. Resolve FAQs (Strictly from secrets for privacy)
    faq_data = []
    if "faq" in secrets_data and "questions" in secrets_data["faq"]:
        faq_data = secrets_data["faq"]["questions"]
    elif "faq" in secrets_data and isinstance(secrets_data["faq"], list):
        faq_data = secrets_data["faq"]

    logger.debug(f"Loaded configuration from secrets: {len(faq_data)} FAQs, {len(personal_context)} profile fields.")
    return faq_data, personal_context, api_key
