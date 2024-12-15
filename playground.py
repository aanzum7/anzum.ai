import streamlit as st
from difflib import SequenceMatcher
import google.generativeai as genai  # type: ignore
import langdetect  # type: ignore


class AnzumAIFAQ:
    def __init__(self):
        self.faq_data = self.load_faq_data()
        self.personal_context = self.load_personal_context()

    def load_faq_data(self):
        """Load FAQ data from Streamlit secrets."""
        try:
            faq_data = st.secrets["faq_data"]
            return {q: a for q, a in (line.split("::") for line in faq_data.splitlines())}
        except Exception as e:
            raise ValueError(f"Error loading FAQ data from secrets: {e}")

    def load_personal_context(self):
        """Load personal context from Streamlit secrets."""
        try:
            return st.secrets["personal_context"]
        except Exception as e:
            raise ValueError(f"Error loading personal context from secrets: {e}")

    def get_faq_data(self):
        """Returns all FAQ data."""
        return self.faq_data


class TanvirAnzumAI:
    def __init__(self):
        self.faq_data = st.secrets["faq_data"]
        self.personal_context = st.secrets["personal_context"]
        self.api_key = st.secrets["genAI_api_key"]

    def generate_answer(self, user_input):
        """Generate AI response using Gemini AI based on user input and context."""
        try:
            # Combine FAQ context and personal context
            context = f"FAQ Context: {self.faq_data}\nPersonal Context: {self.personal_context}"

            # Detect the language of the user input
            language = langdetect.detect(user_input)

            # Configure Generative AI with the API key
            genai.configure(api_key=self.api_key)

            # Set generation parameters
            generation_config = {
                "temperature": 0.5,  # Lower temperature for factual consistency
                "top_p": 0.9,
                "max_output_tokens": 512,  # Enough space for detailed content
            }

            # Create the model
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",  # Or your preferred model
                generation_config=generation_config
            )

            # Start a new chat session for each request
            chat_session = model.start_chat()

            # Construct the enhanced prompt
            prompt = (
                f"Based on Tanvir Anzum's profile and expertise, answer the following question.\n"
                f"FAQ Context: {context}\nUser Input: {user_input}\n\n"
                "Act as an AI version of Tanvir Anzum and generate a response as if you were him. "
                "Provide a detailed, professional answer in the same language as the user input, "
                "preserving the context of the question and profile."
            )

            # Send the prompt to the model
            response = chat_session.send_message(prompt)

            if response and response.text:
                # Return the generated response
                return response.text.strip(), None
            else:
                return None, "No response generated."

        except Exception as e:
            return None, f"Error generating response: {e}"


class AnzumAIChatbot:
    def __init__(self, faq_context, tanvir_ai):
        self.context = []
        self.faq_context = faq_context
        self.tanvir_ai = tanvir_ai

    def handle_chatbot_response(self, user_query):
        """
        Generates a chatbot response by finding the most similar FAQ question and using context.
        The chatbot will return an FAQ reference if relevant, or fall back to AI-generated answers.
        """
        most_similar_question = None
        highest_similarity = 0

        for question in self.faq_context.keys():
            similarity = SequenceMatcher(None, user_query.lower(), question.lower()).ratio()
            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_question = question

        # If there's a good match, return the FAQ response
        if highest_similarity > 0.5:  # Adjusted threshold for more flexibility
            response = (
                f"I found this FAQ answer that might help you: '{most_similar_question}'\n\n"
                f"{self.faq_context[most_similar_question]}"
            )
            return response

        # Otherwise, use Gemini AI to generate a response
        ai_answer, error = self.tanvir_ai.generate_answer(user_query)
        if error:
            return f"Error: {error}"
        return ai_answer


# Streamlit UI
def run_streamlit_app():
    st.title("Anzum.AI - Tanvir Anzum’s AI Assistant")
    st.write("Welcome! You can explore FAQs or chat with the AI assistant. Feel free to ask any questions.")

    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Initialize TanvirAI and AnzumAIChatbot
    faq_instance = AnzumAIFAQ()
    faq_data = faq_instance.get_faq_data()
    tanvir_ai = TanvirAnzumAI()
    chatbot_instance = AnzumAIChatbot(faq_context=faq_data, tanvir_ai=tanvir_ai)

    # Sidebar for FAQ with search feature and default selection
    st.sidebar.title("FAQ")
    faq_search = st.sidebar.text_input("Search FAQ questions...")
    filtered_faq = [faq for faq in faq_data.keys() if faq_search.lower() in faq.lower()] if faq_search else list(
        faq_data.keys())

    # Set the first FAQ as default if available
    selected_faq = st.sidebar.selectbox("Select a FAQ question:", [""] + filtered_faq, index=1 if filtered_faq else 0)

    if selected_faq:
        st.sidebar.write(f"**Anzum.ai:** {faq_data[selected_faq]}")

    # Chatbot
    st.header("Chat with the Anzum.AI Assistant")

    # Clear chat functionality
    if st.button("Clear Chat"):
        st.session_state.chat_history = []

    # Chat interface
    def submit_query():
        if st.session_state.user_query:
            # Generate chatbot response
            bot_response = chatbot_instance.handle_chatbot_response(st.session_state.user_query)

            # Update chat history
            st.session_state.chat_history.append((st.session_state.user_query, bot_response))

            # Clear input field
            st.session_state.user_query = ""

    # Text input with Enter key submission
    user_query = st.text_input("Your message:", key="user_query", on_change=submit_query)

    # Submit button for manual submission
    if st.button("Submit"):
        submit_query()

    # Display chat history (show the latest message at the top)
    for user_msg, bot_msg in reversed(st.session_state.chat_history):
        st.write(f"**You:** {user_msg}")
        st.write(f"**Anzum.AI:** {bot_msg}")

    st.write("**Tip**: Use the FAQ section in the sidebar for quick answers!")


if __name__ == "__main__":
    run_streamlit_app()
