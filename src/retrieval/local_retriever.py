from typing import List, Dict
from src.embeddings.vector_store import VectorStore
from transformers import pipeline
import torch

class LocalRAGRetriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        
        # Use a free local model from Hugging Face
        print("🤖 Loading local LLM (this may take a moment)...")
        
        # Try different models based on available memory
        try:
            # Small, fast model - good for most machines
            self.generator = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            print("✅ Loaded DialoGPT-medium")
        except:
            try:
                # Even smaller fallback
                self.generator = pipeline(
                    "text-generation", 
                    model="distilgpt2",
                    max_length=200
                )
                print("✅ Loaded DistilGPT2 (fallback)")
            except Exception as e:
                print(f"❌ Could not load local model: {e}")
                print("💡 Consider using Ollama or check internet connection")
                raise
    
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
        prompt = f"""Based on the following information about The Door church, please answer this question: {query}

Context:
{context[:1000]}  # Limit context length

Answer:"""
        
        try:
            # Generate response
            result = self.generator(
                prompt,
                max_length=len(prompt.split()) + 50,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )
            
            # Extract just the answer part
            full_response = result[0]['generated_text']
            answer = full_response[len(prompt):].strip()
            
            return answer if answer else "I couldn't generate a response based on the available information."
            
        except Exception as e:
            return f"Sorry, I encountered an error generating a response: {str(e)}"
    
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
    
    retriever = LocalRAGRetriever(vector_store)
    
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