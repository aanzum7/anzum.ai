# ──────────────────────────────────────────────────────────────────────────────
# file: app.py (Unified Agentic Development Kit Playground)
# ──────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import os
import sys
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher

import toml
import streamlit as st
import google.generativeai as genai

# ──────────────────────────────────────────────────────────────────────────────
# 1. CORE LOGGING & CONFIGURATION LAYER
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AgenticDevelopmentKit")

class ConfigError(Exception):
    """Raised when configuration cannot be loaded or is invalid."""

# Global Mock Data to ensure the app works seamlessly right out of the box
DEFAULT_MOCK_SECRETS = {
    "genai": {"api_key": os.getenv("GEMINI_API_KEY", "MOCK_KEY_DISREGARD_IF_PROD")},
    "personal": {
        "data": {
            "name": "Tanvir Anzum",
            "role": "AI Engineer & Software Architect",
            "location": "Dhaka, Bangladesh",
            "bio": "Specialized in building scalable production-grade LLM applications and agentic workflows.",
            "github": "https://github.com/tanviranzum",
            "linkedin": "https://linkedin.com/in/tanviranzum"
        }
    },
    "faq": {
        "questions": [
            {
                "category": "Experience",
                "question": "What is Tanvir's primary area of expertise?",
                "answer": "Tanvir specializes in Agentic AI workflows, LLM fine-tuning, RAG pipelines, and backend software engineering."
            },
            {
                "category": "Projects",
                "question": "Can I see his recent open-source work?",
                "answer": "Yes! You can view Tanvir's open-source implementations on his GitHub profile (https://github.com/tanviranzum)."
            },
            {
                "category": "Contact",
                "question": "How can I get in touch with Tanvir?",
                "answer": "You can connect with him directly on LinkedIn or schedule an engineering sync via his portfolio links."
            }
        ]
    }
}

def load_configuration() -> Tuple[List[Dict[str, Any]], Dict[str, Any], str]:
    """
    Attempts to read .streamlit/secrets.toml. 
    Gracefully falls back to mock data with a warning banner if not present.
    """
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if not os.path.exists(secrets_path):
        logger.warning("Secrets file not found. Initializing ADK Playground with demo environment data.")
        st.sidebar.warning("⚠️ Running in Demo Sandbox mode with Mock Data.")
        s = DEFAULT_MOCK_SECRETS
        return s["faq"]["questions"], s["personal"]["data"], s["genai"]["api_key"]

    try:
        secrets = toml.load(secrets_path)
        faq_data = secrets["faq"]["questions"]
        personal_context = secrets["personal"]["data"]
        api_key = secrets["genai"]["api_key"]
        return faq_data, personal_context, api_key
    except Exception as e:
        logger.error(f"Malformed secrets tracking: {e}. Reverting to fallback config.")
        st.sidebar.error(f"Failed to compile configurations: {e}")
        s = DEFAULT_MOCK_SECRETS
        return s["faq"]["questions"], s["personal"]["data"], s["genai"]["api_key"]

# ──────────────────────────────────────────────────────────────────────────────
# 2. AGENT TOOLS & REASONING SERVICES
# ──────────────────────────────────────────────────────────────────────────────
class FAQRetrievalTool:
    """Deterministic Vector-like fuzzy router used directly as an LLM Function Tool."""
    def __init__(self, faq_list: List[Dict[str, Any]]):
        self.faq_list = faq_list

    def search_faq(self, query: str, threshold: float = 0.55) -> Dict[str, Any]:
        """
        Scans registered vector database/FAQ nodes for semantic string matches.
        
        Args:
            query: The extracted user search intent.
            threshold: Minimum matching confidence ratio.
        """
        best_match = None
        best_answer = None
        highest_score = 0.0
        target = query.lower().strip()

        for item in self.faq_list:
            question = str(item.get("question", "")).lower()
            score = SequenceMatcher(None, target, question).ratio()
            if score > highest_score:
                highest_score = score
                best_match = item.get("question")
                best_answer = item.get("answer")

        if highest_score >= threshold:
            return {"status": "success", "found": True, "question": best_match, "answer": best_answer, "confidence": round(highest_score, 2)}
        return {"status": "success", "found": False, "message": "No explicit FAQ override discovered."}


@dataclass
class AgentTrace:
    """Logs runtime agent lifecycle iterations for the developer layout panels."""
    event_type: str
    payload: Any
    timestamp: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, default=str)


class AutonomousOrchestrator:
    """
    Advanced Orchestrator featuring dynamic multi-tool structural matching execution
    and real-time execution trace reporting.
    """
    def __init__(self, api_key: str, personal_context: Dict[str, Any], faq_tool: FAQRetrievalTool):
        self.api_key = api_key
        self.personal_context = personal_context
        self.faq_tool = faq_tool
        self.traces: List[AgentTrace] = []
        self._init_gemini_client()

    def _init_gemini_client(self):
        if not self.api_key or self.api_key == "MOCK_KEY_DISREGARD_IF_PROD":
            self.model = None
            return
        try:
            genai.configure(api_key=self.api_key)
            # Declaring capabilities explicitly using Function Call configurations
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                generation_config={
                    "temperature": st.session_state.get("param_temp", 0.3),
                    "top_p": st.session_state.get("param_top_p", 0.95),
                    "max_output_tokens": st.session_state.get("param_max_tokens", 800),
                }
            )
        except Exception as e:
            logger.exception("Failed to establish Agent engine cluster link.")
            self.model = None

    def execute_agent_loop(self, user_prompt: str, system_instruction: str) -> str:
        """
        Executes a classic Agentic Loop: 
        1. Context validation -> 2. Query Routing Tool Strategy -> 3. Execution -> 4. Synthesis
        """
        self.traces.clear()
        import datetime
        ts = lambda: datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]

        self.traces.append(AgentTrace("InputReceived", {"prompt": user_prompt}, ts()))

        # Step 1: Execute Autonomous Fuzzy-Matching Pipeline
        self.traces.append(AgentTrace("ToolCall_Invoked", {"tool": "FAQRetrievalTool", "input": user_prompt}, ts()))
        tool_res = self.faq_tool.search_faq(user_prompt)
        self.traces.append(AgentTrace("ToolCall_Completed", {"output": tool_res}, ts()))

        # Step 2: Formulate dynamic multi-agent perspective execution context
        injected_context = f"Personal Base Data Context:\n{json.dumps(self.personal_context, indent=2)}\n\n"
        if tool_res.get("found"):
            injected_context += f"Verified Ground Truth Match Found:\nQ: {tool_res['question']}\nA: {tool_res['answer']}\n"
        else:
            injected_context += "Verified Ground Truth Match Found: None. Rely on system profile knowledge context directly.\n"

        # Step 3: Call Model for synthesis / reasoning
        if not self.model:
            # Safe localized deterministic fallback when API keys are absent
            self.traces.append(AgentTrace("FallbackExecution", "No active Gemini cluster connection. Direct compilation applied.", ts()))
            if tool_res.get("found"):
                return f"🤖 [Local Demo Agent Direct Output]\n\n{tool_res['answer']}"
            return f"🤖 [Local Demo Agent Direct Output]\n\nHello! I am an agent representing Tanvir. I received your message: '{user_prompt}'. Please add a real Gemini API Key into your Streamlit configurations or system environment variables to test complex cross-reasoning generation patterns."

        # Step 4: LLM Generation Inference Pipeline
        try:
            full_compiled_prompt = (
                f"{system_instruction}\n\n"
                f"--- RUNTIME CONTEXT ENGINE ---\n"
                f"{injected_context}\n\n"
                f"--- USER RUNTIME INPUT ---\n"
                f"{user_prompt}"
            )
            
            self.traces.append(AgentTrace("LLM_Inference_Start", {"engine": "gemini-2.5-flash-lite"}, ts()))
            response = self.model.generate_content(full_compiled_prompt)
            output_text = response.text.strip() if (response and response.text) else "Error: Empty sequence returned."
            
            self.traces.append(AgentTrace("LLM_Inference_End", {"output_preview": output_text[:120] + "..."}, ts()))
            return output_text
        except Exception as e:
            self.traces.append(AgentTrace("Pipeline_Execution_Failure", {"exception": str(e)}, ts()))
            return f"⚠️ Orchestrator execution collapsed under trace path execution: {e}"

# ──────────────────────────────────────────────────────────────────────────────
# 3. STREAMLIT INTERACTIVE GRAPHICAL ADK UI SURFACE
# ──────────────────────────────────────────────────────────────────────────────
def init_session_states():
    """Initializes multi-agent global control parameters."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "🤖 System agent initial state online. Diagnostics connection confirmed. Ask me anything regarding Tanvir's portfolio framework."}
        ]
    if "agent_traces" not in st.session_state:
        st.session_state.agent_traces = []
    if "system_prompt_override" not in st.session_state:
        st.session_state.system_prompt_override = (
            "Instructions for AI Agent:\n"
            "- You are Tanvir Anzum's digital twin AI representative.\n"
            "- Speak with engineering precision, keeping statements clean, concise, and professional.\n"
            "- Render interactive Markdown lists or structured layout panels when providing external references."
        )

def main():
    st.set_page_config(
        page_title="anzum.ai - ADK Playground",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    init_session_states()

    # --- TOP HERO LOGO HEADER ---
    st.markdown("""
        <div style='padding: 1rem; border-bottom: 1px solid #383b40; margin-bottom: 2rem;'>
            <h1 style='margin: 0; color: #00f0ff; font-family: monospace;'>⚡ anzum.ai // Agentic Development Kit</h1>
            <p style='margin: 5px 0 0 0; color: #8a909a; font-size: 0.9rem;'>Production Multi-Agent Workspace Playground & Knowledge Router</p>
        </div>
    """, unsafe_allow_html=True)

    # Load global system configuration variables
    faq_data, personal_context, api_key = load_configuration()
    faq_tool = FAQRetrievalTool(faq_data)
    orchestrator = AutonomousOrchestrator(api_key, personal_context, faq_tool)

    # ──────────────────────────────────────────────────────────────────────────
    # SIDEBAR CONTROL: LLM HYPERPARAMETERS & ENGINE METRICS
    # ──────────────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🛠️ ADK Core Engine Params")
        st.session_state.param_temp = st.slider("Temperature Range", 0.0, 1.0, 0.3, 0.05)
        st.session_state.param_top_p = st.slider("Nucleus Sampling (Top P)", 0.1, 1.0, 0.95, 0.05)
        st.session_state.param_max_tokens = st.number_input("Max Output Tokens Buffer", 128, 4096, 768, 64)
        
        st.divider()
        st.markdown("### 📋 Agent Profiles & Vector Memory Base")
        with st.expander("Show Injected Personal Profile"):
            st.json(personal_context)
        with st.expander("Show Registered FAQ Vectors"):
            st.json(faq_data)
            
        if st.button("🧹 Flush Conversation Cache", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": "Conversation system storage cleared. Re-initializing engine diagnostics."}]
            st.session_state.agent_traces = []
            st.rerun()

    # ──────────────────────────────────────────────────────────────────────────
    # MAIN ADK PLAYGROUND VIEW: 2-COLUMN DUAL DASHBOARD INTERACTIVE DESIGN
    # ──────────────────────────────────────────────────────────────────────────
    workspace_col, telemetry_col = st.columns([1.1, 0.9], gap="medium")

    # --- LEFT PANEL: INTERACTIVE APPLICATION PLATFORM ---
    with workspace_col:
        st.markdown("### 🖥️ Live Agent Workspace")
        
        # Adjustable System Instructions directly on the UI dashboard surface
        with st.expander("⚙️ System Agent Architecture Instruction Configuration", expanded=False):
            st.session_state.system_prompt_override = st.text_area(
                "Modify active system personality framing agent rules:",
                value=st.session_state.system_prompt_override,
                height=150
            )

        st.markdown("---")
        # Chat container UI loop block
        chat_container = st.container(height=450)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Input box capture targeting orchestrator triggers
        if user_query := st.chat_input("Dispatch agentic instruction or query..."):
            with chat_container:
                st.chat_message("user").markdown(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})

            # Process prompt through multi-agent reasoning track loops
            with st.spinner("Executing Orchestrator Track Routing..."):
                agent_response = orchestrator.execute_agent_loop(
                    user_prompt=user_query,
                    system_instruction=st.session_state.system_prompt_override
                )

            # Store computed steps for developer workspace telemetry output views
            st.session_state.agent_traces = orchestrator.traces
            
            with chat_container:
                st.chat_message("assistant").markdown(agent_response)
            st.session_state.messages.append({"role": "assistant", "content": agent_response})
            st.rerun()

    # --- RIGHT PANEL: TELEMETRY TRACING & REAL-TIME LOG DEEP DIVE ---
    with telemetry_col:
        st.markdown("### 🧬 Real-Time Agent Telemetry Inspector")
        st.caption("Inspect live multi-agent execution graphs, state decisions, and trace call stacks.")
        
        if not st.session_state.agent_traces:
            st.info("No active traces captured. Query the agent engine to output dynamic tool tracking context logs.")
        else:
            for idx, trace in enumerate(st.session_state.agent_traces):
                # Color code status logs for immediate production readability
                color_map = {
                    "InputReceived": "🔵",
                    "ToolCall_Invoked": "🟡",
                    "ToolCall_Completed": "🟢",
                    "LLM_Inference_Start": "🚀",
                    "LLM_Inference_End": "⚡",
                    "FallbackExecution": "🟣"
                }
                emoji = color_map.get(trace.event_type, "⚙️")
                
                with st.expander(f"{emoji} Step {idx+1}: {trace.event_type} [{trace.timestamp}]", expanded=(idx == len(st.session_state.agent_traces)-1)):
                    st.code(trace.to_json(), language="json")

        # Static ADK Diagnostics Overview Metrics Block
        st.markdown("### 📊 ADK Component Architecture Map")
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric(label="Active External Tool Interfaces", value="1 (FAQ Fuzzy Router)")
        with metric_col2:
            st.metric(label="System Target Backbone Model", value="gemini-2.5-flash-lite")

if __name__ == "__main__":
    main()
