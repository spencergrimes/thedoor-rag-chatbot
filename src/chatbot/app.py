import streamlit as st
import sys
import os

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
    layout="wide"
)

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

def main():
    st.title("🏛️ The Door Church Chatbot")
    st.markdown("Ask me anything about The Door church in Maple Grove, MN!")
    
    # Choose LLM based on availability (widget outside cached function)
    llm_choice = st.sidebar.selectbox(
        "Choose LLM:",
        ["Ollama (Free)", "OpenAI (Paid)"],
        index=0
    )
    
    retriever = initialize_rag_system(llm_choice)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm here to help you learn about The Door church. You can ask me about services, beliefs, getting involved, leadership, or anything else you'd like to know!"
            }
        ]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about The Door church..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Searching for relevant information..."):
                result = retriever.answer_question(prompt)
                
                response = result['answer']
                st.markdown(response)
                
                if result['sources']:
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(result['sources'], 1):
                            st.write(f"{i}. **{source['title']}**")
                            st.write(f"   URL: {source['url']}")
                            st.write(f"   Relevance: {source['similarity']:.2f}")
                
                with st.expander("🔍 Response Details"):
                    st.write(f"**Confidence Score:** {result['confidence']:.2f}")
                    st.write(f"**Documents Used:** {result['context_used']}")
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.sidebar.markdown("## About This Chatbot")
    st.sidebar.markdown("""
    This chatbot uses RAG (Retrieval-Augmented Generation) to answer questions about The Door church based on their website content.
    
    **Features:**
    - 🔍 Searches relevant church information
    - 🤖 Generates contextual responses
    - 📊 Shows confidence scores
    - 📚 Provides source references
    """)
    
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Hello! I'm here to help you learn about The Door church. You can ask me about services, beliefs, getting involved, leadership, or anything else you'd like to know!"
            }
        ]
        st.experimental_rerun()

if __name__ == "__main__":
    main()