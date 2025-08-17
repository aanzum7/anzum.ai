# ──────────────────────────────────────────────────────────────────────────────
# file: services/agentic_ai.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Dict, Optional
import logging

import google.generativeai as genai
import langdetect

from services.logger import get_logger

logger = get_logger(__name__)

class AgenticAI:
    """
    Thin wrapper around Google Gemini for chat-style responses.

    - Initializes client once.
    - Provides a resilient `generate_response` with a one-time retry.
    """

    def __init__(self, api_key: str, context: Dict):
        self.api_key = api_key
        self.context = context
        self.model = None
        self.chat_session = None
        self._configure_ai()

    def _configure_ai(self):
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                generation_config={
                    "temperature": 0.5,
                    "top_p": 0.9,
                    "max_output_tokens": 512,
                },
            )
            self.chat_session = self.model.start_chat()
            logger.info("Gemini model configured and chat session started.")
        except Exception as e:
            logger.exception("Failed to configure AI.")
            raise

    def reset(self):
        """Reset chat (use after 'Start Over')."""
        logger.info("Resetting chat session.")
        self.chat_session = self.model.start_chat()

    @staticmethod
    def _detect_language(text: str) -> str:
        try:
            return langdetect.detect(text)
        except langdetect.lang_detect_exception.LangDetectException:
            return "unknown"

    def _build_prompt(self, user_input: str, input_language: Optional[str]) -> str:
        return (
            "Based on Tanvir Anzum's profile and expertise, answer the following question.\n"
            f"FAQ Context: {self.context.get('faq')}\n"
            f"Personal Context: {self.context.get('personal')}\n"
            f"Detected Language: {input_language}\n"
            f"User Input: {user_input}\n\n"
            "Act as an AI version of Tanvir Anzum and respond in a simple, concise, and conversational manner, "
            "like a human chat, while maintaining professionalism and the given context. "
            "If relevant, you may include links to Tanvir's work or projects."
        )

    def generate_response(self, user_input: str) -> str:
        try:
            input_language = self._detect_language(user_input)
            prompt = self._build_prompt(user_input, input_language)

            response = self.chat_session.send_message(prompt)
            if response and hasattr(response, "text") and response.text:
                return response.text.strip()

            # Retry once on empty/invalid
            logger.warning("Empty/invalid response. Retrying once with a fresh chat session.")
            self.reset()
            response_retry = self.chat_session.send_message(prompt)
            if response_retry and hasattr(response_retry, "text") and response_retry.text:
                return response_retry.text.strip()

            return "🤖 Sorry, I couldn't generate a response."

        except Exception as e:
            logger.exception("Error generating response.")
            return f"⚠️ Error: {e}"

