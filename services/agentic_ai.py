# ──────────────────────────────────────────────────────────────────────────────
# file: services/agentic_ai.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from typing import Dict
import logging

import google.generativeai as genai

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
                model_name="gemini-2.0-flash-lite",
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

    def _build_prompt(self, user_input: str) -> str:
        return (
            f"Based on Tanvir Anzum's profile and expertise (from context links), answer the user's question.\n\n"
            f"FAQ Context:\n{self.context.get('faq')}\n\n"
            f"Personal Context:\n{self.context.get('personal')}\n\n"
            f"User Question:\n{user_input}\n\n"
            "Instructions for AI:\n"
            "- Respond as an AI version of Tanvir Anzum.\n"
            "- Keep answers simple, concise, conversational, and professional.\n"
            "- Reply in the style and format asked by the user.\n"
            "- If relevant, provide links as interactive buttons with clear labels and URLs that the user can click directly.\n"
            "- Only include links that are contextually appropriate."
        )

    def generate_response(self, user_input: str) -> str:
        try:
            prompt = self._build_prompt(user_input)

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
