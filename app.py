import streamlit as st
import sys
import os

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.embeddings.vector_store import VectorStore
from src.retrieval.local_retriever import LocalRAGRetriever
from config.config import Config

st.set_page_config(
    page_title="The Door Church RAG Chatbot",
    page_icon="🏛️",
    layout="wide"
)

@st.cache_resource
def initialize_rag_system():
    """Initialize the RAG system with local models for demo"""
    try:
        vector_store = VectorStore(
            db_path=Config.VECTOR_DB_PATH,
            embedding_model=Config.EMBEDDING_MODEL
        )
        
        retriever = LocalRAGRetriever(vector_store)
        return retriever
    except Exception as e:
        st.error(f"Failed to initialize RAG system: {str(e)}")
        return None

def main():
    st.title("🏛️ The Door Church RAG Chatbot")
    st.markdown("**Portfolio Demo**: RAG system built with Python, ChromaDB, and Transformers")
    
    # Add portfolio context
    with st.expander("🔍 About This Demo"):
        st.markdown("""
        This is a **Retrieval-Augmented Generation (RAG)** chatbot demonstration that answers questions about The Door church.
        
        **Tech Stack:**
        - 🕷️ **Web Scraping**: Playwright for data collection
        - 📊 **Vector Database**: ChromaDB for semantic search
        - 🤖 **Embeddings**: Sentence-transformers for text vectorization
        - 🧠 **LLM**: Local Hugging Face models for generation
        - 🚀 **Framework**: Streamlit for the web interface
        
        **Key Features:**
        - Semantic search across church content
        - Source attribution and confidence scoring
        - Local processing (no API keys required)
        """)
    
    retriever = initialize_rag_system()
    
    if not retriever:
        st.error("Could not initialize the RAG system. Please check the setup.")
        return
    
    # Sample questions for demo
    st.sidebar.markdown("## 💡 Try These Questions:")
    sample_questions = [
        "What time are Sunday services?",
        "What is The Door's mission?",
        "How can I get involved?",
        "Where is the church located?",
        "What programs do you offer?"
    ]
    
    for q in sample_questions:
        if st.sidebar.button(q, key=f"sample_{q}"):
            st.session_state.sample_question = q
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hi! I'm a RAG chatbot demo that can answer questions about The Door church. Try asking me anything about their services, mission, or programs!"
            }
        ]
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle sample question click
    if hasattr(st.session_state, 'sample_question'):
        prompt = st.session_state.sample_question
        del st.session_state.sample_question
    else:
        prompt = st.chat_input("Ask about The Door church...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching knowledge base..."):
                result = retriever.answer_question(prompt)
                
                response = result['answer']
                st.markdown(response)
                
                # Show sources and metrics for demo
                col1, col2 = st.columns(2)
                
                with col1:
                    if result['sources']:
                        with st.expander("📚 Sources Used"):
                            for i, source in enumerate(result['sources'], 1):
                                st.write(f"**{i}. {source['title']}**")
                                st.write(f"Relevance: {source['similarity']:.2f}")
                
                with col2:
                    with st.expander("📊 RAG Metrics"):
                        st.metric("Confidence Score", f"{result['confidence']:.2f}")
                        st.metric("Sources Retrieved", result['context_used'])
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Footer for portfolio
    st.markdown("---")
    st.markdown("**💼 Portfolio Demo** | Built by [Your Name] | [GitHub Link] | [LinkedIn]")

if __name__ == "__main__":
    main()