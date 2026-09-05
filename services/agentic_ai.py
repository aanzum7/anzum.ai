# ──────────────────────────────────────────────────────────────────────────────
# file: services/agentic_ai.py
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import time
import warnings
from typing import Any, Dict, Generator, List, Optional

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*google.generativeai.*")

import google.generativeai as genai
from google.ai import generativelanguage as glm
from google.api_core import exceptions as google_exceptions

from config.settings import (
    DEFAULT_GEMINI_MODEL,
    GEMINI_FALLBACK_MODELS,
    GENERATION_CONFIG,
    MODEL_QUOTA_COOLDOWN_SECONDS,
    SUGGESTION_CHIPS,
)
from services.cache_manager import SemanticResponseCache, get_response_cache
from services.logger import get_logger
from services.mcp_server import MCPServer, create_mcp_server
from services.rate_limiter import get_funky_glitch_response

logger = get_logger(__name__)


def format_model_label(model_name: str) -> str:
    """Format model technical string into a clean UI label."""
    cleaned = model_name.replace("models/", "")
    parts = cleaned.split("-")
    return " ".join(
        p.capitalize() if not any(c.isdigit() for c in p) else p for p in parts
    )


class AgenticAI:
    """
    State-of-the-art AI Digital Twin and Portfolio Guide of Tanvir Anzum.
    Features:
    - Decoupled Model Context Protocol (MCP) Knowledge Server (no prompt token bloat).
    - Autonomous Gemini function calling / tool use.
    - Automatic multi-model failover across all free Gemini text models on 429 quota exhaustion.
    - True token streaming with multi-turn conversation memory.
    """

    def __init__(
        self,
        api_key: str,
        context: Dict[str, Any],
        mcp_server: Optional[MCPServer] = None,
        cache: Optional[SemanticResponseCache] = None,
    ):
        self.api_key = api_key
        self.context = context

        # 1. Initialize or accept MCP Knowledge Server
        if mcp_server:
            self.mcp_server = mcp_server
        else:
            personal = context.get("personal", {})
            faqs = context.get("faq", [])
            self.mcp_server = create_mcp_server(personal, faqs)

        # 2. Initialize and pre-seed Semantic Response Cache
        if cache:
            self.cache = cache
        else:
            self.cache = get_response_cache()
            self.cache.preseed(
                faq_data=context.get("faq", []),
                suggestion_chips=SUGGESTION_CHIPS,
                personal_context=context.get("personal", {}),
            )

        # 3. Ultra-lean system instruction (saves ~95% input tokens per call)
        self.system_instruction = self._format_lean_instruction()

        # 4. Build prioritized candidate model pool
        pool: List[str] = []
        if DEFAULT_GEMINI_MODEL:
            pool.append(DEFAULT_GEMINI_MODEL)
        for m in GEMINI_FALLBACK_MODELS:
            if m not in pool:
                pool.append(m)

        self.model_pool: List[str] = pool
        self._active_model_name: str = pool[0] if pool else DEFAULT_GEMINI_MODEL
        self._session_model: Optional[str] = None
        self._exhausted_models: Dict[str, float] = {}  # model -> cooldown expiration timestamp

        self.model: Optional[genai.GenerativeModel] = None
        self.chat_session = None

        self._configure_ai()

    def _format_lean_instruction(self) -> str:
        """
        Ultra-lean system instruction.
        Eliminates token bloat by delegating all facts to MCP knowledge tools.
        """
        return (
            "You are the official AI Digital Twin and Portfolio Guide of Tanvir Anzum.\n"
            "Your purpose is to answer visitor questions regarding Tanvir's experience, background, research, projects, skills, and vision.\n\n"
            "=== TONALITY & IDENTITY ===\n"
            "- Speak in the first person ('I', 'my') as Tanvir Anzum.\n"
            "- Maintain an articulate, humble, innovative, and professional tone.\n"
            "- CRITICAL RULE: Keep answers SHORT, DIRECT, and CONCISE (typically 2 to 4 sentences or 2 to 3 brief bullet points).\n"
            "- NEVER generate long walls of text or encyclopedic explanations.\n"
            "- If links or projects are relevant, provide a 1-line summary with the direct clickable markdown link.\n\n"
            "=== AGENTIC MEMORY TOOLS ===\n"
            "You have access to verified MCP knowledge tools ('search_knowledge_base', 'get_profile_topic', 'get_verified_faq').\n"
            "Whenever a visitor asks about my background, work at Prothom Alo / Brain Station 23, recommendation engines, "
            "TUHH Master's in Hamburg, technical skills, research, or contact information, call the appropriate tool to retrieve "
            "the precise facts before answering."
        )

    def _dispatch_tool_call(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Route tool call from Gemini to the MCP Knowledge Server."""
        logger.info(f"Agentic Tool Execution: {tool_name} with args: {args}")
        try:
            if tool_name == "search_knowledge_base":
                query = str(args.get("query", ""))
                return self.mcp_server.search_knowledge_base(query=query)
            elif tool_name == "get_profile_topic":
                topic = str(args.get("topic", ""))
                return self.mcp_server.get_profile_topic(topic=topic)
            elif tool_name == "get_verified_faq":
                question = str(args.get("question", args.get("question_or_topic", "")))
                return self.mcp_server.get_verified_faq(question_or_topic=question)
            else:
                return self.mcp_server.search_knowledge_base(query=str(args))
        except Exception as e:
            logger.debug(f"Error executing MCP tool '{tool_name}': {e}")
            return f"Error querying knowledge base: {e}"

    def _init_chat(self, model_name: str, history: Optional[List] = None) -> bool:
        """Initialize or switch the Gemini chat session to a specified model with MCP tools."""
        try:
            tools = self.mcp_server.get_python_tools() if self.mcp_server else None
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=GENERATION_CONFIG,
                system_instruction=self.system_instruction,
                tools=tools,
            )
            self.chat_session = self.model.start_chat(history=history or [])
            self._session_model = model_name
            logger.debug(f"Initialized Gemini chat session on model '{model_name}' with MCP tools.")
            return True
        except Exception as e:
            logger.debug(f"Model '{model_name}' tools notice: {e}. Attempting tool-less fallback...")
            try:
                # Fallback without tools if model does not support tool calling
                self.model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=GENERATION_CONFIG,
                    system_instruction=self.system_instruction,
                )
                self.chat_session = self.model.start_chat(history=history or [])
                self._session_model = model_name
                return True
            except Exception as e2:
                logger.debug(f"Failed fallback init for model '{model_name}': {e2}")
                self.model = None
                self.chat_session = None
                self._session_model = None
                return False

    def _configure_ai(self):
        """Initial configuration using the top candidate model."""
        try:
            genai.configure(api_key=self.api_key)
            candidates = self.get_candidate_models()
            configured = False
            for cand in candidates:
                if self._init_chat(cand):
                    self._active_model_name = cand
                    configured = True
                    break

            if not configured:
                self._init_chat(DEFAULT_GEMINI_MODEL)
                self._active_model_name = DEFAULT_GEMINI_MODEL

            logger.info(f"Gemini AI ready with primary active model: {self._active_model_name}")
        except Exception as e:
            logger.exception(f"Failed to configure Gemini AI: {e}")
            raise

    @property
    def active_model_name(self) -> str:
        """Name of the currently active model."""
        return self._active_model_name

    @property
    def active_model_label(self) -> str:
        """Formatted human-friendly label of the active model."""
        return format_model_label(self._active_model_name)

    def reset(self):
        """Reset chat session state."""
        logger.debug("Resetting Gemini chat session.")
        if self.model:
            self.chat_session = self.model.start_chat(history=[])

    def _is_quota_or_recoverable_error(self, e: Exception) -> bool:
        """Check if an exception indicates quota exhaustion, rate limiting, or temporary model issue."""
        if isinstance(
            e,
            (
                google_exceptions.ResourceExhausted,
                google_exceptions.TooManyRequests,
                google_exceptions.DeadlineExceeded,
                google_exceptions.ServiceUnavailable,
                google_exceptions.NotFound,
                google_exceptions.InternalServerError,
            ),
        ):
            return True

        err_str = str(e).lower()
        recoverable_markers = [
            "429",
            "503",
            "504",
            "404",
            "resource_exhausted",
            "resourceexhausted",
            "quota exceeded",
            "rate limit",
            "quota",
            "deadline expired",
            "exceeded your current quota",
            "no longer available",
            "overloaded",
        ]
        return any(marker in err_str for marker in recoverable_markers)

    def get_candidate_models(self) -> List[str]:
        """Return prioritized list of models, putting active model first and respecting cooldowns."""
        now = time.time()
        self._exhausted_models = {
            m: exp for m, exp in self._exhausted_models.items() if exp > now
        }

        available: List[str] = []
        cooling_down: List[str] = []

        if self._active_model_name in self.model_pool:
            if self._active_model_name in self._exhausted_models:
                cooling_down.append(self._active_model_name)
            else:
                available.append(self._active_model_name)

        for m in self.model_pool:
            if m not in available and m not in cooling_down:
                if m in self._exhausted_models:
                    cooling_down.append(m)
                else:
                    available.append(m)

        return available if available else cooling_down

    def stream_response(self, user_input: str) -> Generator[str, None, None]:
        """
        Yield streaming text chunks for st.write_stream().
        Checks semantic query cache first. If not cached, executes agentic MCP tool
        calling if factual details are needed, and automatically fails over across
        free Gemini text models on 429 quota exhaustion.
        All exceptions are captured quietly with zero technical error leaks in the UI.
        """
        # 1. Check semantic cache (Fast path: instant response, 0 API tokens used)
        cached_result = self.cache.get(user_input)
        if cached_result:
            cached_text, score = cached_result
            logger.debug(f"Serving query from semantic cache (similarity: {score:.2f})")
            for chunk in self.cache.stream_cached_response(cached_text):
                yield chunk
            return

        candidate_models = self.get_candidate_models()
        prior_history = list(self.chat_session.history) if self.chat_session else []

        last_exception = None
        collected_chunks: List[str] = []

        for model_candidate in candidate_models:
            if (
                self._session_model != model_candidate
                or not self.chat_session
                or not self.model
            ):
                initialized = self._init_chat(model_candidate, history=prior_history)
                if not initialized:
                    self._exhausted_models[model_candidate] = (
                        time.time() + MODEL_QUOTA_COOLDOWN_SECONDS
                    )
                    continue

            yielded_any = False
            try:
                logger.debug(f"Attempting response generation on '{model_candidate}'...")
                response = self.chat_session.send_message(user_input, stream=True)

                pending_fn_call = None
                for chunk in response:
                    if not chunk.candidates:
                        continue
                    parts = chunk.candidates[0].content.parts
                    for p in parts:
                        if p.function_call:
                            pending_fn_call = p.function_call
                        elif p.text:
                            yielded_any = True
                            collected_chunks.append(p.text)
                            yield p.text

                # If the model requested an MCP Knowledge tool call
                if pending_fn_call:
                    fn_name = pending_fn_call.name
                    fn_args = dict(pending_fn_call.args)
                    tool_result = self._dispatch_tool_call(fn_name, fn_args)

                    # Supply tool response back to chat session and stream final synthesis
                    fn_part = glm.Part(
                        function_response=glm.FunctionResponse(
                            name=fn_name,
                            response={"result": tool_result},
                        )
                    )
                    stream_res = self.chat_session.send_message(fn_part, stream=True)
                    for final_chunk in stream_res:
                        if final_chunk and hasattr(final_chunk, "text") and final_chunk.text:
                            yielded_any = True
                            collected_chunks.append(final_chunk.text)
                            yield final_chunk.text

                if not yielded_any:
                    fallback_text = (
                        "I'm here to help with any questions regarding Tanvir's background, "
                        "projects, or technical skills! Feel free to ask me anything specific."
                    )
                    yield fallback_text
                    return

                # Successfully completed turn -> cache result for similar future asking
                self._active_model_name = model_candidate
                full_text = "".join(collected_chunks)
                if full_text:
                    self.cache.set(user_input, full_text)
                logger.debug(f"Turn completed successfully on '{model_candidate}'.")
                return

            except Exception as e:
                last_exception = e
                if yielded_any:
                    logger.debug(f"Stream interrupted mid-generation on '{model_candidate}': {e}")
                    # Conclude gracefully without exposing stack traces or error logs
                    yield "\n\n*(Feel free to ask if you'd like more details on this!)*"
                    return

                if self._is_quota_or_recoverable_error(e):
                    self._exhausted_models[model_candidate] = (
                        time.time() + MODEL_QUOTA_COOLDOWN_SECONDS
                    )
                    logger.debug(
                        f"Model '{model_candidate}' reached quota limit. "
                        f"Failing over to next available Gemini text model..."
                    )
                    continue
                else:
                    logger.debug(f"Non-recoverable error on '{model_candidate}': {e}")
                    continue

        logger.debug(f"All candidate models exhausted. Last error: {last_exception}")
        # Return witty / funky fallback instead of raw error log
        yield get_funky_glitch_response()

    def generate_response(self, user_input: str) -> str:
        """Synchronous response generation."""
        return "".join(list(self.stream_response(user_input)))
