# anzum.ai — Personalized AI Digital Twin

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://anzum-ai.streamlit.app/?embed_options=dark_theme)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Powered by Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.5%20Flash-blue)](https://ai.google.dev/)

A state-of-the-art, personalized AI Digital Twin and portfolio assistant for **Tanvir Anzum**. The application delivers real-time conversational responses powered by **Google Gemini 2.5 Flash**, verified knowledge base matching, interactive question chips, and a modern glassmorphic interface.

---

## ✨ Key Features

- **⚡ Real-Time Streaming Chat**: Instant typewriter-style response streaming via Gemini 2.5 Flash.
- **🔍 Intelligent Knowledge Base Matching**: Hybrid semantic search (token intersection, Jaccard similarity, sequence ratio) for verified FAQ answers.
- **💎 Premium Glassmorphism UI**:
  - Dark mode with glowing radial accents and Google Fonts (`Outfit` & `Plus Jakarta Sans`).
  - Active pulse status indicators (`AI Twin Online`).
  - Interactive quick-prompt suggestion chips.
  - Collapsible FAQ knowledge cards with category badges and instant search filtering.
- **🧠 Persistent Multi-Turn Memory**: Conversational memory preserved across Streamlit reruns.
- **🌐 Dynamic Profile & Social Integration**: Dynamic link cards, current focus badges, research dossiers, and contact drawer.

---

## 🛠️ Tech Stack & Architecture

```
anzum.ai/
├── .streamlit/
│   └── secrets.toml        # STRICTLY PRIVATE: API key, FAQs & Personal Profile Data [GITIGNORED]
├── config/
│   ├── __init__.py
│   ├── config.toml         # Theme tokens, server & client settings
│   └── settings.py         # Application metadata, paths, model & UI constants
├── logo/
│   └── aanzum7.png         # Profile avatar & favicon
├── services/
│   ├── __init__.py
│   ├── agentic_ai.py       # Gemini 2.5 Flash wrapper with system_instruction & streaming
│   ├── config.py           # Cached loader reading credentials & context securely
│   ├── faq.py              # Semantic FAQ retriever with hybrid heuristics
│   └── logger.py           # Centralized structured logger
├── ui/
│   ├── __init__.py
│   ├── chat.py             # Chat interface with streaming & quick prompt chips
│   ├── faq_view.py         # Searchable knowledge base with category tabs
│   ├── sidebar.py          # Dynamic profile card with glowing avatar & social links
│   └── styles.py           # Global CSS design tokens & animations
├── aanzum.py               # Main application entry point
├── playground.py           # Developer sandbox runner
├── Procfile                # Heroku deployment configuration
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

---

## 🚀 Quick Start

### 1. Clone the repository:
```bash
git clone https://github.com/aanzum7/anzum.ai.git
cd anzum.ai
```

### 2. Set up virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 4. Configure Secrets:
Create `.streamlit/secrets.toml` with your Gemini API key (or set `GEMINI_API_KEY` in your environment):
```toml
[genai]
api_key = "YOUR_GEMINI_API_KEY"
```

> **Note**: Public portfolio content and FAQs are cleanly maintained in `data/personal_info.json` and `data/faqs.json`. You can easily edit those JSON files to update your profile or add questions without touching secrets!

### 5. Run the application:
```bash
streamlit run aanzum.py
```

---

## 🌐 Live Demo & Deployment

- **Live Application:** [anzum.ai](https://anzum-ai.streamlit.app/?embed_options=dark_theme)
- **Deployment Ready:** Supports direct deployment to **Streamlit Community Cloud** (via Secrets settings) or **Heroku** (via `Procfile`).

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
