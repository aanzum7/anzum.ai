import streamlit as st # type: ignore
from difflib import SequenceMatcher
import google.generativeai as genai # type: ignore
import langdetect # type: ignore
import toml # type: ignore
from typing import Dict, Tuple, Optional

# Configure logging (optional)
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgenticAI:
    """A class to manage context-driven AI responses using Agentic capabilities."""
    def __init__(self, api_key: str, context: Dict):
        self.api_key = api_key
        self.context = context
        self.configure_ai()

    def configure_ai(self):
        """Configure the AI model."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
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
        """Generate a conversational response based on the provided user input."""
        try:
            # Detect the language of the user input
            input_language = langdetect.detect(user_input)

            # Create a prompt that ensures the AI responds as Tanvir Anzum
            prompt = (
                f"FAQ Context: {self.context['faq']}\n"
                f"Personal Context: {self.context['personal']}\n"
                f"User Input: {user_input}\n\n"
                "Act as if you are Tanvir Anzum himself. Respond simply, conversationally, and professionally. "
                f"The user's input is in {input_language}, but respond in English while maintaining the style of the input.\n"
                "If relevant, feel free to include additional links from Tanvir's work or projects or social profiles."
            )
            response = self.chat_session.send_message(prompt)
            return response.text.strip() if response and response.text else "I'm sorry, I couldn't generate a response."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error: {e}"

class FAQHandler:
    """Handles FAQ retrieval and matching based on user input."""
    def __init__(self, faq_data: Dict):
        self.faq_data = faq_data

    def find_similar_question(self, user_input: str, threshold: float = 0.65) -> Tuple[Optional[str], Optional[str]]:
        """Find the most similar FAQ question to the user input."""
        most_similar_question = None
        highest_similarity = 0

        for question in self.faq_data.keys():
            similarity = SequenceMatcher(None, user_input.lower(), question.lower()).ratio()
            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_question = question

        if highest_similarity >= threshold:
            return most_similar_question, self.faq_data[most_similar_question]
        return None, None

class AnzumAIApp:
    """Main application logic for anzum.ai."""
    def __init__(self):
        self.faq_data, self.personal_context, self.api_key = self.load_configuration()
        self.faq_handler = FAQHandler(self.faq_data)
        self.agentic_ai = AgenticAI(
            api_key=self.api_key, 
            context={"faq": self.faq_data, "personal": self.personal_context}
        )

    def load_configuration(self) -> Tuple[Dict, Dict, str]:
        """Load configuration from secrets."""
        try:
            secrets = toml.load(".streamlit/secrets.toml")
            faq_data = {faq['question']: faq['answer'] for faq in secrets['faq']['questions']}
            personal_context = secrets['personal']['data']
            api_key = secrets['genai']['api_key']
            return faq_data, personal_context, api_key
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise FileNotFoundError(f"Error loading configuration: {e}")

    def process_user_query(self, user_query: str) -> str:
        """Process user input and provide an appropriate response."""
        faq_question, faq_answer = self.faq_handler.find_similar_question(user_query)
        if faq_answer:
            return f"FAQ Match: '{faq_question}'\n\n{faq_answer}"
        return self.agentic_ai.generate_response(user_query)

    def run(self):
        # Main section
        st.title("Hey, I'm **anzum.ai**! 💥")
        st.write(
            "I'm the AI clone of **Tanvir Anzum**, here to share my work, journey, and aspirations. Let’s get started! 🌟"
        )

        # Sidebar for FAQ
        st.sidebar.title("FAQs")

        # Search box for FAQ filtering
        search_query = st.sidebar.text_input("Search FAQs:")

        # Filter FAQ list dynamically based on search query
        filtered_faqs = [q for q in self.faq_data if search_query.lower() in q.lower()] if search_query else list(self.faq_data.keys())

        # Dropdown for filtered FAQs, defaulting to the first matching result
        if filtered_faqs:
            selected_faq = st.sidebar.selectbox(
                "Explore what’s on the minds of other professionals:",
                filtered_faqs,
                index=0  # Default to the first matching FAQ
            )

            # Display the content for the selected FAQ
            st.sidebar.markdown(f"### {selected_faq}")
            st.sidebar.write(f"**Answer:** {self.faq_data[selected_faq]}")
        else:
            # Placeholder message when no FAQs are found
            st.sidebar.write("No matching FAQs found. Try another search.")

        # Chat interface
        st.header("Chat with anzum.ai")

        # Initialize session state for chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Chat interaction
        def submit_query():
            if st.session_state.user_query:
                with st.spinner("Generating response..."):
                    response = self.process_user_query(st.session_state.user_query)
                    st.session_state.chat_history.append({
                        "user_query": st.session_state.user_query,
                        "bot_response": response,
                        "feedback": None  # Initialize feedback as None
                    })
                    st.session_state.user_query = ""

        # Start chat section
        st.subheader("Start Chat:")
        user_query = st.text_input("What's on your mind?", key="user_query", on_change=submit_query)

        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.chat_history = []

        # Display chat history with feedback for each response
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**You:** {chat['user_query']}")
            st.markdown(f"**anzum.ai:** {chat['bot_response']}")

            # Feedback for each response
            feedback = st.radio(
                "Was this response helpful?",
                options=["👍", "👎"],
                index=None,  # No default selection
                key=f"feedback_{st.session_state.chat_history.index(chat)}"
            )
            if feedback:
                chat["feedback"] = feedback
                logger.info(f"Feedback for response: {feedback}")

        # Footer with tips
        st.write("---")
        st.markdown(
            """
            **Tip:** Type keywords in the FAQ search to find relevant answers quickly!  
            """
        )

if __name__ == "__main__":
    try:
        app = AnzumAIApp()
        app.run()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        logger.error(f"Application error: {e}")