# ──────────────────────────────────────────────────────────────────────────────
# file: ui/sidebar.py
# ──────────────────────────────────────────────────────────────────────────────
import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("Hey, I'm anzum.ai! 💥")
        st.caption(" 🤖 Your AI guide to Tanvir Anzum's **work, journey, and aspirations.**")

        st.markdown(
            """
            <div style='font-size: 14px; font-weight: normal;'>
            Powered by <strong>Google Gemini AI</strong>, I can answer questions about Tanvir’s <strong>career, research, projects, and consulting</strong>.<br/>
            Just ask — <strong>Let’s get started!</strong> 🌟
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.title("👨‍💻 Tanvir Anzum")
        st.caption("AI & Data Researcher | Business & Growth Strategist | ML/NLP-Based Recommendation Specialist")

        st.markdown(
            """
            <div style='font-size: 14px; font-weight: normal;'>
            Passionate about turning <strong>data into actionable insights</strong> and building intelligent systems.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
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
            """,
            unsafe_allow_html=True,
        )

