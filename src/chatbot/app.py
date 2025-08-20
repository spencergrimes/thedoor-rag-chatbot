import streamlit as st
import sys
import os
import time

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.embeddings.vector_store import VectorStore
from src.retrieval.retriever import RAGRetriever
from src.retrieval.ollama_retriever import OllamaRAGRetriever
from config.config import Config

st.set_page_config(
    page_title="The Door Church Chatbot",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_path = os.path.join(project_root, "static", "gemini_style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback inline CSS if file doesn't exist
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@300;400;500;600&family=Inter:wght@300;400;500;600&display=swap');
        
        :root {
            --primary-blue: #1a73e8;
            --light-blue: #e8f0fe;
            --text-primary: #202124;
            --text-secondary: #5f6368;
            --background: #fafafa;
            --surface: #ffffff;
            --border: #e8eaed;
            --shadow: 0 1px 6px rgba(32,33,36,.28);
            --border-radius: 12px;
        }
        
        .main .block-container {
            padding-top: 2rem;
            max-width: 900px;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}
        
        .app-header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 1.5rem 0;
            background: linear-gradient(135deg, var(--surface) 0%, #f8f9fa 100%);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }
        
        .app-title {
            font-family: 'Google Sans', 'Inter', sans-serif;
            font-size: 2.5rem;
            font-weight: 500;
            color: var(--text-primary);
            margin: 0;
        }
        
        .app-subtitle {
            font-family: 'Google Sans', 'Inter', sans-serif;
            font-size: 1.1rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }
        </style>
        """, unsafe_allow_html=True)

@st.cache_resource
def get_vector_store():
    """Get the vector store (cached)"""
    return VectorStore(
        db_path=Config.VECTOR_DB_PATH,
        embedding_model=Config.EMBEDDING_MODEL
    )

def initialize_rag_system(llm_choice: str):
    """Initialize RAG system based on LLM choice"""
    vector_store = get_vector_store()
    
    if llm_choice == "Ollama (Free)":
        try:
            retriever = OllamaRAGRetriever(vector_store)
            st.sidebar.success("✅ Using Ollama (Free)")
            return retriever
        except Exception as e:
            st.sidebar.error(f"Ollama not available: {str(e)}")
            st.sidebar.info("Install Ollama: brew install ollama")
            st.stop()
    else:
        if not Config.OPENAI_API_KEY:
            st.sidebar.error("Please set your OPENAI_API_KEY in the .env file")
            st.stop()
        
        try:
            retriever = RAGRetriever(vector_store, Config.OPENAI_API_KEY)
            st.sidebar.success("✅ Using OpenAI")
            return retriever
        except Exception as e:
            st.sidebar.error(f"OpenAI error: {str(e)}")
            st.stop()

def render_google_header():
    """Render Google-style header"""
    st.markdown("""
    <div class="google-header">
        <div class="google-logo">The Door Church Search</div>
    </div>
    """, unsafe_allow_html=True)

def render_ai_overview(answer, sources, confidence, is_loading=False):
    """Render Google-style AI Overview"""
    if is_loading:
        st.markdown("""
        <div class="loading-overview">
            <div class="loading-spinner"></div>
            <div class="loading-text">Generating AI Overview...</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Create source links
    source_links_html = ""
    for i, source in enumerate(sources[:5], 1):
        source_links_html += f"""
        <a href="{source['url']}" class="ai-source-link" target="_blank">
            <span class="ai-source-number">{i}</span>
            {source['title'][:30]}...
        </a>
        """
    
    overview_html = f"""
    <div class="ai-overview">
        <div class="ai-overview-header">
            <div class="ai-overview-icon">AI</div>
            <h3 class="ai-overview-title">AI Overview</h3>
        </div>
        <div class="ai-overview-content">
            {answer}
        </div>
        <div class="ai-sources">
            <div class="ai-sources-title">Sources</div>
            <div class="ai-source-links">
                {source_links_html}
            </div>
        </div>
    </div>
    """
    
    st.markdown(overview_html, unsafe_allow_html=True)

def render_search_results(sources):
    """Render Google-style search results"""
    st.markdown('<div class="search-results-list">', unsafe_allow_html=True)
    
    for i, source in enumerate(sources, 1):
        # Clean URL for display
        display_url = source['url'].replace('https://', '').replace('http://', '')
        if len(display_url) > 50:
            display_url = display_url[:47] + "..."
        
        result_html = f"""
        <div class="search-result">
            <div class="result-header">
                <div class="result-favicon"></div>
                <span class="result-url">{display_url}</span>
            </div>
            <a href="{source['url']}" class="result-title" target="_blank">
                {source['title']}
            </a>
            <p class="result-snippet">
                Content relevance to your question...
            </p>
            <div class="result-confidence">
                Relevance: {source['similarity']:.0%}
            </div>
        </div>
        """
        st.markdown(result_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_related_questions():
    """Render related questions section"""
    related_questions = [
        "What time are Sunday services at The Door?",
        "How can I get involved at The Door church?",
        "What is The Door's mission and beliefs?",
        "Where is The Door church located?",
        "What programs does The Door offer?"
    ]
    
    questions_html = """
    <div class="related-questions">
        <h3 class="related-questions-title">People also ask</h3>
    """
    
    for question in related_questions:
        questions_html += f"""
        <div class="related-question" onclick="document.querySelector('.stTextInput input').value='{question}'">
            <p class="related-question-text">{question}</p>
            <span class="related-question-arrow">▼</span>
        </div>
        """
    
    questions_html += "</div>"
    st.markdown(questions_html, unsafe_allow_html=True)

def main():
    # Load CSS
    load_css()
    
    # Override with Google Search CSS
    css_path = os.path.join(project_root, "static", "google_search_style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Render Google-style header
    render_google_header()
    
    # Sidebar for LLM selection
    with st.sidebar:
        st.title("⚙️ Settings")
        llm_choice = st.selectbox(
            "Choose AI Model:",
            ["Ollama (Free)", "OpenAI (Paid)"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("**About The Door Church Search**")
        st.markdown("AI-powered search for The Door church information using RAG technology.")
    
    retriever = initialize_rag_system(llm_choice)
    
    # Main search container
    st.markdown('<div class="search-results">', unsafe_allow_html=True)
    
    # Get search query with integrated search icon
    query = st.text_input(
        "Search The Door church...",
        placeholder="What would you like to know about The Door church?",
        label_visibility="collapsed"
    )
    
    # Initialize session state for current query
    if "current_query" not in st.session_state:
        st.session_state.current_query = ""
    if "search_results" not in st.session_state:
        st.session_state.search_results = None
    
    # Handle new search
    if query and query != st.session_state.current_query:
        st.session_state.current_query = query
        
        # Show loading state
        render_ai_overview("", [], 0, is_loading=True)
        
        # Get search results
        with st.spinner(""):
            result = retriever.answer_question(query)
            st.session_state.search_results = result
        
        # Clear the loading state and rerun
        st.rerun()
    
    # Display results if available
    if st.session_state.search_results and st.session_state.current_query:
        result = st.session_state.search_results
        
        # AI Overview section
        render_ai_overview(
            result['answer'],
            result['sources'],
            result['confidence']
        )
        
        # Search results
        if result['sources']:
            render_search_results(result['sources'])
        
        # Related questions
        render_related_questions()
    
    else:
        # Show initial state with suggested searches
        st.markdown("""
        <div style="text-align: center; margin: 60px 0;">
            <h2 style="color: #5f6368; font-weight: 400; font-size: 20px; margin-bottom: 30px;">
                Search The Door church information
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Show popular searches as buttons
        st.markdown("**Popular searches:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🕐 Sunday service times"):
                st.session_state.current_query = "What time are Sunday services?"
                st.rerun()
            if st.button("📍 Church location"):
                st.session_state.current_query = "Where is The Door church located?"
                st.rerun()
                
        with col2:
            if st.button("🤝 How to get involved"):
                st.session_state.current_query = "How can I get involved at The Door?"
                st.rerun()
            if st.button("ℹ️ Church mission"):
                st.session_state.current_query = "What is The Door's mission?"
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()