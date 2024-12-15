# anzum.ai - Personalized AI Assistant

A Streamlit-based web application that provides personalized responses, FAQs, and advanced AI-generated answers. The app leverages Generative AI (Gemini) to deliver context-aware, accurate, and professional replies based on predefined FAQs and personal context.

## Features
- **FAQ Matching**: Matches user queries with the most relevant FAQ and provides predefined answers.
- **Generative AI Responses**: Uses Gemini AI to generate detailed, context-aware responses for unmatched queries.
- **Language Detection**: Ensures responses are in the same language as the user query.
- **Customizable Context**: Easily update FAQs and personal data for tailored responses.

## Prerequisites
Before running the app, ensure you have the following:
- Python 3.7 or higher
- `pip` (Python package installer)
- A valid **Generative AI API key** (e.g., Gemini)

## Installation
### 1. Clone the repository:
```bash
git clone https://github.com/aanzum7/anzum.ai.git
cd anzum.ai
```

### 2. Set up a Python virtual environment (optional but recommended):
```bash
python -m venv venv
```

### 3. Activate the virtual environment:
- On Windows:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### 4. Install dependencies:
```bash
pip install -r requirements.txt
```

### 5. Run the app:
```bash
streamlit run app.py
```

This will start the Streamlit app and open it in your default web browser.

## Usage
1. **Enter Your Query**: Type a question or query in the text box.
2. **FAQ Matching**: If a match is found in the FAQs, a predefined answer is displayed.
3. **AI-Generated Response**: For unmatched queries, the AI generates a response using the context provided.
4. **Multi-Language Support**: Queries and responses are supported in the same language as detected.

## Customization
- **Updating FAQs**: Modify the configuration to add or update FAQs.
- **Enhancing Context**: Adjust the data provided to improve the AI’s understanding of your domain.
- **Adjusting AI Parameters**: Customize temperature, max tokens, or other generation settings in the `generate_answer` method of `TanvirAnzumAI`.

## Dependencies
This project uses the following Python libraries:
- `streamlit`: Framework for creating web apps.
- `requests`: For API and web requests.
- `google.generativeai`: Google’s Generative AI API for generating answers.
- `langdetect`: For detecting the language of user queries.
- `toml`: For handling configuration data.
- `difflib`: For matching user queries with FAQ questions.

Install dependencies with:
```bash
pip install -r requirements.txt
```

## Troubleshooting
- **FAQ Not Found**: Ensure the configuration file is correctly set up.
- **API Key Issues**: Verify the API key used in the application.
- **Language Mismatch**: The app may fail to detect certain languages if `langdetect` encounters ambiguous input.
- **Gemini AI Issues**: Check your API limits and connection if no responses are generated.

## Demo
Check out the live demo: [anzum.ai](https://anzum-ai.streamlit.app/?embed_options=dark_theme)

## Repository
Explore the codebase: [GitHub Repository](https://github.com/aanzum7/anzum.ai/tree/master)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
