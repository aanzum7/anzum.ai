# ──────────────────────────────────────────────────────────────────────────────
# file: services/agentic_ai.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import warnings
from typing import Any, Dict, Generator, Optional

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*google.generativeai.*")

import google.generativeai as genai

from config.settings import DEFAULT_GEMINI_MODEL, GENERATION_CONFIG
from services.logger import get_logger

logger = get_logger(__name__)

class AgenticAI:
    """
    Intelligent Assistant persona wrapper around Google Gemini.
    Configured with native system_instruction and streaming output capabilities.
    """

    def __init__(self, api_key: str, context: Dict[str, Any]):
        self.api_key = api_key
        self.context = context
        self.model: Optional[genai.GenerativeModel] = None
        self.chat_session = None
        self._configure_ai()

    def _format_context(self) -> str:
        """Format personal and FAQ context cleanly for the system instruction."""
        personal = self.context.get("personal", {})
        faq = self.context.get("faq", [])

        personal_str = json.dumps(personal, indent=2, default=str)
        faq_str = json.dumps(faq, indent=2, default=str)

        return (
            "You are the official AI Digital Twin and Portfolio Guide of Tanvir Anzum.\n"
            "Your purpose is to answer visitor questions regarding Tanvir's experience, background, research, projects, skills, and vision.\n\n"
            "=== TONALITY & IDENTITY ===\n"
            "- Speak in the first person ('I', 'my') as Tanvir Anzum.\n"
            "- Maintain an articulate, humble, innovative, and professional tone.\n"
            "- CRITICAL RULE: Keep answers SHORT, DIRECT, and CONCISE (typically 2 to 4 sentences or 2 to 3 brief bullet points).\n"
            "- NEVER generate long walls of text or encyclopedic explanations.\n"
            "- If links or projects are relevant, provide a 1-line summary with the direct clickable markdown link.\n\n"
            f"=== VERIFIED BACKGROUND & CONTEXT (CONFIDENTIAL) ===\n{personal_str}\n\n"
            f"=== KNOWLEDGE BASE & FAQS ===\n{faq_str}\n"
        )

    def _configure_ai(self):
        try:
            genai.configure(api_key=self.api_key)
            system_instruction = self._format_context()

            self.model = genai.GenerativeModel(
                model_name=DEFAULT_GEMINI_MODEL,
                generation_config=GENERATION_CONFIG,
                system_instruction=system_instruction,
            )
            self.chat_session = self.model.start_chat(history=[])
            logger.debug("Gemini model initialized with system instruction.")
        except Exception as e:
            logger.exception(f"Failed to configure Gemini AI: {e}")
            raise

    def reset(self):
        """Reset chat session state."""
        logger.debug("Resetting Gemini chat session.")
        if self.model:
            self.chat_session = self.model.start_chat(history=[])

    def stream_response(self, user_input: str) -> Generator[str, None, None]:
        """
        Yield streaming text chunks for st.write_stream().
        Falls back gracefully with retry if necessary.
        """
        try:
            if not self.chat_session:
                self.reset()

            response = self.chat_session.send_message(user_input, stream=True)
            has_content = False
            for chunk in response:
                if chunk and hasattr(chunk, "text") and chunk.text:
                    has_content = True
                    yield chunk.text

            if not has_content:
                yield "I apologize, but I couldn't generate a clear response for that query. Could you try rephrasing?"

        except Exception as e:
            logger.exception("Error during streaming response generation.")
            yield f"⚠️ *I encountered an issue connecting to Gemini: {e}*"

    def generate_response(self, user_input: str) -> str:
        """Synchronous response generation."""
        return "".join(list(self.stream_response(user_input)))
