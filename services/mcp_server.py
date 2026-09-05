# ──────────────────────────────────────────────────────────────────────────────
# file: services/mcp_server.py
# ──────────────────────────────────────────────────────────────────────────────
"""
Model Context Protocol (MCP) Knowledge Server for anzum.ai.

Provides structured, indexed memory retrieval for Tanvir Anzum's AI Twin,
decoupling raw context from input prompts to drastically reduce token usage
and prevent rate limit/quota exhaustion on the Gemini API.

Can be imported directly as a service or executed as a standalone JSON-RPC
MCP server over stdio for external MCP clients (Cursor, Claude, Antigravity).
"""
from __future__ import annotations

import json
import re
import sys
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set, Tuple

from services.logger import get_logger

logger = get_logger(__name__)

STOPWORDS: Set[str] = {
    "a", "about", "an", "and", "are", "as", "at", "be", "by", "can", "could",
    "do", "does", "for", "from", "how", "i", "in", "is", "it", "me", "my",
    "of", "on", "or", "tell", "the", "to", "was", "what", "when", "where",
    "which", "who", "why", "with", "would", "you", "your"
}


def _tokenize(text: str) -> List[str]:
    """Extract lowercase words."""
    return re.findall(r"\b\w+\b", text.lower())


def _significant_tokens(text: str) -> Set[str]:
    """Extract non-stopword tokens."""
    tokens = _tokenize(text)
    meaningful = {w for w in tokens if w not in STOPWORDS}
    return meaningful if meaningful else set(tokens)


class MCPKnowledgeBase:
    """
    Structured Memory & MCP Tool provider for Tanvir Anzum.
    Indexes personal history, skills, research, and FAQs into discrete memory cards.
    """

    def __init__(self, personal_context: Dict[str, Any], faq_data: List[Dict[str, Any]]):
        self.raw_personal = personal_context or {}
        self.raw_faq = faq_data or []
        self.memory_cards: Dict[str, Dict[str, Any]] = {}
        self._build_memory_index()

    def _build_memory_index(self):
        """Parse raw context into organized, semantic memory cards."""
        personal = self.raw_personal

        # 1. Summary & Current Status
        summary_text = (
            f"Tanvir Anzum: {personal.get('introduction', 'Data Analytics & AI specialist')}. "
            f"Current status: {personal.get('professional_current_role', '')}. "
            f"Goals: {personal.get('aspirations', '')}"
        )
        self.memory_cards["summary"] = {
            "title": "Tanvir Anzum Summary & Current Status",
            "keywords": {"summary", "who", "tanvir", "anzum", "about", "bio", "overview", "introduction", "current"},
            "content": summary_text,
        }

        # 2. Work Experience
        exp_text = (
            f"Current Role: {personal.get('professional_current_role', '')}\n"
            f"Previous Roles: {personal.get('professional_previous_role', '')}\n"
            "Key Achievements:\n"
            "- Prothom Alo: Built collaborative filtering & Word2Vec recommender engine for 20M+ readers, "
            "cutting memory footprint ~50% and runtime from 90 to 10 mins. Built Gemini AI article tagger.\n"
            "- Brain Station 23: Developed Streamlit EDA & ML readiness dashboards for enterprise clients.\n"
            "- Sheba Platform Ltd: 3 years building operational data pipelines and business intelligence analytics."
        )
        self.memory_cards["experience"] = {
            "title": "Professional Experience & Key Achievements",
            "keywords": {"experience", "work", "job", "career", "prothom", "alo", "brain", "station", "sheba", "recommender", "recommendation", "role", "roles"},
            "content": exp_text,
        }

        # 3. Education & Academics
        edu_text = (
            f"Education Summary: {personal.get('education_summary', '')}\n"
            "- Master's Degree: Incoming Master's in Information and Communication Systems at Hamburg University of Technology (TUHH), Germany.\n"
            "- Bachelor's Degree: BSc in Computer Science and Engineering (CSE) from Daffodil International University (2016-2020).\n"
            "- Professional Executive Education: Advanced Certificate for Management Professionals (ACMP 4.0) at IBA, University of Dhaka."
        )
        self.memory_cards["education"] = {
            "title": "Education & Academic Credentials",
            "keywords": {"education", "academic", "university", "degree", "tuhh", "hamburg", "daffodil", "diu", "iba", "bsc", "masters", "master"},
            "content": edu_text,
        }

        # 4. Technical Skills & Tools
        skills_text = (
            "Core Technical Skills & Stack:\n"
            "- Programming & Data: Python, SQL (MariaDB, MySQL, BigQuery), Pandas, NumPy, Scikit-learn\n"
            "- Machine Learning & AI: Recommendation Systems (Collaborative Filtering, Word2Vec embeddings), Generative AI (Gemini API), NLP\n"
            "- Dashboarding & BI: Streamlit, Looker Studio, Google Analytics 4 (GA4)\n"
            "- MLOps & Tools: Git, GitHub, Docker basics, Linux, Conda, REST APIs"
        )
        self.memory_cards["skills"] = {
            "title": "Technical Stack, Skills & Tools",
            "keywords": {"skills", "tech", "stack", "tools", "python", "sql", "ml", "machine", "learning", "streamlit", "bigquery", "looker", "gemini", "programming"},
            "content": skills_text,
        }

        # 5. Research & Publications
        research_text = (
            f"Interests & Research: {personal.get('interests', '')}\n"
            "Research Focus: Machine Learning, Recommender Systems, Computer Vision, and Natural Language Processing.\n"
            "Publications available on ResearchGate and Google Scholar profile."
        )
        self.memory_cards["research"] = {
            "title": "Research Interests & Publications",
            "keywords": {"research", "publications", "papers", "thesis", "study", "scholar", "researchgate", "nlp", "vision", "scientific"},
            "content": research_text,
        }

        # 6. Hamburg & Werkstudent Opportunities
        hamburg_text = (
            f"Hamburg Opportunities: {personal.get('aspirations', '')}\n"
            "Tanvir is relocating to Hamburg for his Master's at TUHH and is actively seeking a Werkstudent (Working Student) "
            "position in Data Analytics, Business Intelligence, Data Engineering, or Applied AI."
        )
        self.memory_cards["hamburg"] = {
            "title": "Hamburg Relocation & Werkstudent Search",
            "keywords": {"hamburg", "werkstudent", "student", "germany", "relocating", "seeking", "opportunity", "hire", "job", "internship"},
            "content": hamburg_text,
        }

        # 7. Contact & Links
        contact_dict = personal.get("contact", {})
        prof_links = personal.get("professional_links", {})
        soc_links = personal.get("social_links", {})
        contact_text = (
            f"Contact Details:\n"
            f"- Email: {contact_dict.get('email', 'tanviranzum70@gmail.com')}\n"
            f"- Academic Email: {contact_dict.get('edu_email', '')}\n"
            f"- Phone: {contact_dict.get('phone', '')}\n"
            f"- LinkedIn: {prof_links.get('linkedin', 'https://linkedin.com/in/aanzum7')}\n"
            f"- GitHub: {prof_links.get('github', 'https://github.com/aanzum7')}\n"
            f"- Portfolio / Website: {soc_links.get('personal_site', 'https://anzum7.github.io')}\n"
            f"- Streamlit Apps: {prof_links.get('streamlit', 'https://share.streamlit.io/user/aanzum7')}"
        )
        self.memory_cards["contact"] = {
            "title": "Contact Details & Links",
            "keywords": {"contact", "email", "phone", "linkedin", "github", "connect", "reach", "portfolio", "social", "hire", "talk"},
            "content": contact_text,
        }

        logger.debug(f"MCP KnowledgeBase indexed {len(self.memory_cards)} memory cards and {len(self.raw_faq)} FAQs.")

    def search_knowledge_base(self, query: str, max_results: int = 2) -> str:
        """
        MCP Tool: Retrieve the most relevant memory cards and FAQ answers matching a query.
        Returns concise, verified knowledge without token bloat.
        """
        if not query or not query.strip():
            return "No query specified."

        tokens = _significant_tokens(query)
        scored_cards: List[Tuple[float, str, str]] = []

        # 1. Score memory cards
        for key, card in self.memory_cards.items():
            card_title = card["title"]
            card_content = card["content"]
            keywords = card["keywords"]

            # Overlap score
            overlap = len(tokens.intersection(keywords))
            ratio = SequenceMatcher(None, query.lower(), card_title.lower()).ratio()
            content_lower = card_content.lower()

            containment = sum(1.0 for t in tokens if t in content_lower)
            score = (overlap * 2.0) + (ratio * 1.5) + containment

            if score > 0.8:
                scored_cards.append((score, card_title, card_content))

        # 2. Check FAQs for direct match
        for faq in self.raw_faq:
            q_str = str(faq.get("question", ""))
            a_str = str(faq.get("answer", ""))
            q_tokens = _significant_tokens(q_str)
            intersection = len(tokens.intersection(q_tokens))
            seq_ratio = SequenceMatcher(None, query.lower(), q_str.lower()).ratio()
            score = (intersection * 2.2) + (seq_ratio * 2.0)

            if score > 1.2:
                scored_cards.append((score, f"FAQ: {q_str}", a_str))

        if not scored_cards:
            # Fallback to summary
            summary = self.memory_cards.get("summary", {})
            return f"[{summary.get('title', 'Overview')}]: {summary.get('content', '')}"

        # Sort descending by score
        scored_cards.sort(key=lambda x: x[0], reverse=True)
        top = scored_cards[:max_results]

        results = [f"=== {title} ===\n{content}" for _, title, content in top]
        return "\n\n".join(results)

    def get_profile_topic(self, topic: str) -> str:
        """
        MCP Tool: Retrieve a specific profile section by topic name.
        Supported topics: 'experience', 'education', 'skills', 'projects', 'contact', 'hamburg', 'summary', 'research'.
        """
        topic_clean = topic.strip().lower()

        # Topic alias mapping
        mapping = {
            "work": "experience",
            "job": "experience",
            "career": "experience",
            "prothom": "experience",
            "brainstation": "experience",
            "academic": "education",
            "university": "education",
            "degree": "education",
            "tuhh": "education",
            "tech": "skills",
            "stack": "skills",
            "tools": "skills",
            "python": "skills",
            "papers": "research",
            "publications": "research",
            "werkstudent": "hamburg",
            "germany": "hamburg",
            "email": "contact",
            "links": "contact",
            "bio": "summary",
            "about": "summary",
        }

        key = mapping.get(topic_clean, topic_clean)
        if key in self.memory_cards:
            card = self.memory_cards[key]
            return f"=== {card['title']} ===\n{card['content']}"

        # Fallback to search
        return self.search_knowledge_base(topic, max_results=1)

    def get_verified_faq(self, question_or_topic: str) -> str:
        """
        MCP Tool: Search verified portfolio FAQs for a direct answer.
        """
        if not question_or_topic or not self.raw_faq:
            return "No matching FAQ found."

        tokens = _significant_tokens(question_or_topic)
        best_faq = None
        best_score = 0.0

        for faq in self.raw_faq:
            q = str(faq.get("question", ""))
            q_tokens = _significant_tokens(q)
            overlap = len(tokens.intersection(q_tokens)) / max(len(tokens), 1)
            ratio = SequenceMatcher(None, question_or_topic.lower(), q.lower()).ratio()
            score = (overlap * 0.6) + (ratio * 0.4)

            if score > best_score:
                best_score = score
                best_faq = faq

        if best_faq and best_score >= 0.45:
            return f"Q: {best_faq.get('question')}\nA: {best_faq.get('answer')}"

        return "No specific verified FAQ matched. Use search_knowledge_base for broader context."

    def get_tools_manifest(self) -> List[Dict[str, Any]]:
        """Return MCP compliant JSON Schema tool declarations."""
        return [
            {
                "name": "search_knowledge_base",
                "description": (
                    "Search Tanvir Anzum's verified knowledge base for facts about his experience, "
                    "recommender system projects, skills, education at TUHH, research, or contact information."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Specific query or keywords to look up in the knowledge base.",
                        }
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_profile_topic",
                "description": (
                    "Retrieve a full specific section of Tanvir's profile. "
                    "Topics: 'experience', 'education', 'skills', 'hamburg', 'research', 'contact', 'summary'."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The section name to retrieve.",
                        }
                    },
                    "required": ["topic"],
                },
            },
            {
                "name": "get_verified_faq",
                "description": "Lookup verified frequently asked questions and official answers about Tanvir Anzum.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question_or_topic": {
                            "type": "string",
                            "description": "The FAQ question or topic.",
                        }
                    },
                    "required": ["question_or_topic"],
                },
            },
        ]


class MCPServer:
    """
    Model Context Protocol (MCP) Server.
    Provides standard MCP JSON-RPC protocol handling and Python function bindings.
    """

    def __init__(self, personal_context: Dict[str, Any], faq_data: List[Dict[str, Any]]):
        self.kb = MCPKnowledgeBase(personal_context=personal_context, faq_data=faq_data)

    # Directly callable Python methods for Gemini tools=[...]
    def search_knowledge_base(self, query: str) -> str:
        """Search Tanvir Anzum's verified knowledge base for facts about his work, skills, projects, or background."""
        return self.kb.search_knowledge_base(query=query)

    def get_profile_topic(self, topic: str) -> str:
        """Retrieve a specific section of Tanvir's profile ('experience', 'education', 'skills', 'hamburg', 'contact', 'summary')."""
        return self.kb.get_profile_topic(topic=topic)

    def get_verified_faq(self, question_or_topic: str) -> str:
        """Lookup verified frequently asked questions and official answers about Tanvir Anzum."""
        return self.kb.get_verified_faq(question_or_topic=question_or_topic)

    def get_python_tools(self) -> List[Any]:
        """Return list of Python callable functions suitable for Google Gemini tools parameter."""
        return [
            self.search_knowledge_base,
            self.get_profile_topic,
            self.get_verified_faq,
        ]

    def handle_jsonrpc(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle standard JSON-RPC 2.0 requests per MCP specification."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "anzum-ai-mcp-server", "version": "1.0.0"},
                    "capabilities": {"tools": {}},
                },
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.kb.get_tools_manifest()},
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            result_text = ""
            if tool_name == "search_knowledge_base":
                result_text = self.search_knowledge_base(query=str(arguments.get("query", "")))
            elif tool_name == "get_profile_topic":
                result_text = self.get_profile_topic(topic=str(arguments.get("topic", "")))
            elif tool_name == "get_verified_faq":
                result_text = self.get_verified_faq(
                    question_or_topic=str(arguments.get("question_or_topic", ""))
                )
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": result_text}]
                },
            }

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not supported: {method}"},
        }

    def run_stdio(self):
        """Run MCP JSON-RPC server loop reading from stdin and writing to stdout."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                res = self.handle_jsonrpc(req)
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
            except Exception as e:
                err_res = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": str(e)},
                }
                sys.stdout.write(json.dumps(err_res) + "\n")
                sys.stdout.flush()


def create_mcp_server(personal_context: Dict[str, Any], faq_data: List[Dict[str, Any]]) -> MCPServer:
    """Factory helper to instantiate an MCPServer."""
    return MCPServer(personal_context=personal_context, faq_data=faq_data)


if __name__ == "__main__":
    # Standalone execution via stdio (e.g. for external MCP clients)
    try:
        from services.config import load_configuration
        faqs, personal, _ = load_configuration()
    except Exception:
        faqs, personal = [], {}

    server = create_mcp_server(personal, faqs)
    server.run_stdio()
