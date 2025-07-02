import streamlit as st
from difflib import SequenceMatcher
import google.generativeai as genai
import langdetect
import toml
from typing import Dict, Tuple, Optional, List
import logging


# ---------------------------
# Logging Setup
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------------------------
# AI Handler
# ---------------------------
class AgenticAI:
    def __init__(self, api_key: str, context: Dict):
        self.api_key = api_key
        self.context = context
        self.configure_ai()

    def configure_ai(self):
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
        except Exception as e:
            logger.error(f"Failed to configure AI: {e}")
            raise

    def generate_response(self, user_input: str) -> str:
        try:
            try:
                input_language = langdetect.detect(user_input)
            except langdetect.lang_detect_exception.LangDetectException:
                input_language = "unknown"

            prompt = (
                f"FAQ Context: {self.context['faq']}\n"
                f"Personal Context: {self.context['personal']}\n"
                f"User Input: {user_input}\n\n"
                "Act as if you are Tanvir Anzum himself. Respond simply, conversationally, and professionally. "
                f"The user's input is in {input_language}, but respond in English while maintaining the tone of the input.\n"
                "If relevant, include links from Tanvir's work or projects. Add appropriate emojis to make it friendlier."
            )
            response = self.chat_session.send_message(prompt)
            return response.text.strip() if response and response.text else "🤖 Sorry, I couldn't generate a response."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"⚠️ Error: {e}"


# ---------------------------
# FAQ Handler
# ---------------------------
class FAQHandler:
    def __init__(self, faq_list: List[Dict]):
        self.faq_list = faq_list

    def find_similar_question(self, user_input: str, threshold: float = 0.65) -> Tuple[Optional[str], Optional[str]]:
        most_similar_question = None
        highest_similarity = 0
        best_answer = None

        for faq in self.faq_list:
            similarity = SequenceMatcher(None, user_input.lower(), faq['question'].lower()).ratio()
            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_question = faq['question']
                best_answer = faq['answer']

        if highest_similarity >= threshold:
            return most_similar_question, best_answer
        return None, None


# ---------------------------
# Main App
# ---------------------------
class AnzumAIApp:
    def __init__(self):
        self.faq_data, self.personal_context, self.api_key = self.load_configuration()
        self.faq_handler = FAQHandler(self.faq_data)
        self.agentic_ai = AgenticAI(
            api_key=self.api_key,
            context={"faq": self.faq_data, "personal": self.personal_context}
        )

    def load_configuration(self) -> Tuple[List[Dict], Dict, str]:
        try:
            secrets = toml.load(".streamlit/secrets.toml")
            faq_data = secrets['faq']['questions']
            personal_context = secrets['personal']['data']
            api_key = secrets['genai']['api_key']
            return faq_data, personal_context, api_key
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise FileNotFoundError(
                f"Configuration loading failed. Ensure `.streamlit/secrets.toml` is present and correct.\nError: {e}"
            )

    def process_user_query(self, user_query: str) -> str:
        faq_question, faq_answer = self.faq_handler.find_similar_question(user_query)
        if faq_answer:
            return f"🔍 **FAQ Match:** *{faq_question}*\n\n{faq_answer}"
        return self.agentic_ai.generate_response(user_query)

    def run(self):
        st.set_page_config(page_title="anzum.ai", layout="wide")

        # ---------------------------
        # Sidebar
        # ---------------------------
        with st.sidebar:
            st.title("Hey, I'm anzum.ai! 💥")
            st.caption(" 🤖 Your AI guide to Tanvir Anzum's **work, journey, and aspirations.**")

            st.markdown("""
                <div style='font-size: 14px; font-weight: normal;'>
                Powered by <strong>Google Gemini AI</strong>, I can answer questions about Tanvir’s <strong>career, research, projects, and consulting</strong>.  
                Just ask — <strong>Let’s get started!</strong> 🌟
                </div>
                """, unsafe_allow_html=True)


            st.title("👨‍💻 Tanvir Anzum")
            st.caption("AI & Data Researcher | Business & Growth Strategist | ML/NLP-Based Recommendation Specialist")

            st.markdown("""
                <div style='font-size: 14px; font-weight: normal;'>
                Passionate about turning <strong>data into actionable insights</strong> and building intelligent systems.
                </div> """, unsafe_allow_html=True)

            st.markdown("""
                <div style='font-size: 14px; font-weight: normal;'>
                <br>
                <a href="https://www.linkedin.com/in/aanzum" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn" width="16" style="vertical-align:middle; margin-right:6px;">
                    <strong>LinkedIn</strong>
                </a>
                &nbsp;&nbsp;
                <a href="https://www.researchgate.net/profile/Tanvir-Anzum" target="_blank">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/5/5e/ResearchGate_icon_SVG.svg" alt="ResearchGate" width="16" style="vertical-align:middle; margin-right:6px;">
                    <strong>Research</strong>
                </a>
                </div>
                """, unsafe_allow_html=True)

        # ---------------------------
        # FAQ Section
        # ---------------------------
        st.subheader("💡 Frequently Asked Questions")

        desired_order = [
            "Experience", "Education", "Research", "Work", "Technologies",
            "Skills", "Projects", "Certificates", "Consulting"
        ]
        existing_categories = list(set(faq['category'] for faq in self.faq_data))
        categories = [cat for cat in desired_order if cat in existing_categories]

        tabs = st.tabs(categories)

        for i, category in enumerate(categories):
            with tabs[i]:
                category_faqs = list(filter(lambda x: x['category'] == category, self.faq_data))
                for faq in category_faqs:
                    with st.expander(f"❓ {faq['question']}"):
                        st.markdown(f"{faq['answer']}")

        st.divider()

        # ---------------------------
        # Chat Section
        # ---------------------------
        st.subheader("💬 Chat with anzum.ai")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display Chat History
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.markdown(chat["user_query"])

            with st.chat_message("assistant"):
                st.markdown(chat["bot_response"])

        # Chat Input
        user_query = st.chat_input("What's on your mind ?")

        if user_query:
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.spinner("Let me craft a thoughtful reply just for you... 🤖"):
                response = self.process_user_query(user_query)

            with st.chat_message("assistant"):
                st.markdown(response)

            st.session_state.chat_history.append({
                "user_query": user_query,
                "bot_response": response
            })

        # ---------------------------
        # Footer Styling
        # ---------------------------
        st.markdown("""
            <style>
            .center-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
                margin-top: 20px;
            }
            .center-button {
                width: 50%;
                min-width: 300px;
                padding: 8px 16px;
                background-color: #f0f2f6;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                text-align: center;
                transition: background-color 0.3s;
            }
            .center-button:hover {
                background-color: #e0e2e6;
            }
            </style>
        """, unsafe_allow_html=True)

        # ---------------------------
        # Footer Logic
        # ---------------------------
        if st.session_state.chat_history:
            st.markdown("<div class='center-container'>", unsafe_allow_html=True)

            # Feedback appears first
            feedback = st.radio(
                "Feedback",
                ["👍", "👎"],
                index=None,
                horizontal=True,
                key="overall_feedback"
            )
            if feedback:
                logger.info(f"Overall Feedback: {feedback}")  

            # Start Over button
            clicked = st.button("🔄 Start Over", use_container_width=True)
            if clicked:
                st.session_state.chat_history = []
                self.agentic_ai.configure_ai()

            st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------
# App Runner
# ---------------------------
if __name__ == "__main__":
    try:
        app = AnzumAIApp()
        app.run()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.error(f"Application error: {e}")
