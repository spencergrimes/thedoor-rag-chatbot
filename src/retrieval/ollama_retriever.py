from typing import List, Dict
from src.embeddings.vector_store import VectorStore
import requests
import json

class OllamaRAGRetriever:
    def __init__(self, vector_store: VectorStore, model: str = "llama3.2:1b"):
        self.vector_store = vector_store
        self.model = model
        self.base_url = "http://localhost:11434"
        
        # Check if Ollama is running
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                print(f"✅ Connected to Ollama (available models: {len(response.json().get('models', []))})")
            else:
                print("⚠️  Ollama not responding - make sure it's installed and running")
        except:
            print("❌ Ollama not found. Install with: brew install ollama")
            print("   Then run: ollama pull llama3.2:1b")
    
    def retrieve_relevant_docs(self, query: str, n_results: int = 5) -> List[Dict]:
        return self.vector_store.search(query, n_results)
    
    def format_context(self, retrieved_docs: List[Dict]) -> str:
        context_parts = []
        for doc in retrieved_docs:
            context_parts.append(f"Source: {doc['metadata']['source_title']}")
            context_parts.append(f"Content: {doc['content']}")
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, context: str) -> str:
        system_prompt = """You are a helpful assistant that answers questions about The Door church in Maple Grove, MN. 
        Use the provided context to answer questions accurately. Keep responses concise and helpful.
        If you cannot find the answer in the context, say so honestly."""
        
        user_prompt = f"""Context about The Door church:
{context[:2000]}

Question: {query}

Please provide a helpful answer based on the context above."""
        
        # Combine system and user prompts for generate API
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 150
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['response']
            else:
                return f"Error from Ollama: {response.status_code}"
                
        except Exception as e:
            return f"Could not connect to Ollama: {str(e)}"
    
    def answer_question(self, query: str, n_docs: int = 3) -> Dict:
        retrieved_docs = self.retrieve_relevant_docs(query, n_docs)
        
        if not retrieved_docs:
            return {
                'answer': "I couldn't find relevant information to answer your question.",
                'sources': [],
                'confidence': 0.0
            }
        
        context = self.format_context(retrieved_docs)
        answer = self.generate_response(query, context)
        
        sources = [
            {
                'title': doc['metadata']['source_title'],
                'url': doc['metadata']['source_url'],
                'similarity': doc['similarity_score']
            }
            for doc in retrieved_docs
        ]
        
        avg_similarity = sum(doc['similarity_score'] for doc in retrieved_docs) / len(retrieved_docs)
        
        return {
            'answer': answer,
            'sources': sources,
            'confidence': avg_similarity,
            'context_used': len(retrieved_docs)
        }

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config.config import Config
    
    vector_store = VectorStore(
        db_path=Config.VECTOR_DB_PATH,
        embedding_model=Config.EMBEDDING_MODEL
    )
    
    retriever = OllamaRAGRetriever(vector_store)
    
    test_questions = [
        "What time are Sunday services?",
        "What is The Door's mission?",
        "How can I get involved?"
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        result = retriever.answer_question(question)
        print(f"A: {result['answer']}")
        print(f"Confidence: {result['confidence']:.2f}")