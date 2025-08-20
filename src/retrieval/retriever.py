from typing import List, Dict
from src.embeddings.vector_store import VectorStore
import openai
from config.config import Config

class RAGRetriever:
    def __init__(self, vector_store: VectorStore, openai_api_key: str):
        self.vector_store = vector_store
        openai.api_key = openai_api_key
        self.client = openai.OpenAI(api_key=openai_api_key)
    
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
        Use the provided context to answer questions accurately. If you cannot find the answer in the context, 
        say so honestly. Focus on being helpful and informative about The Door's services, beliefs, and community."""
        
        user_prompt = f"""Context about The Door church:
{context}

Question: {query}

Please provide a helpful answer based on the context above."""
        
        try:
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=Config.MAX_TOKENS,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"I'm sorry, I encountered an error while generating a response: {str(e)}"
    
    def answer_question(self, query: str, n_docs: int = 5) -> Dict:
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
    
    if not Config.OPENAI_API_KEY:
        print("Please set your OPENAI_API_KEY in the .env file")
        exit(1)
    
    vector_store = VectorStore(
        db_path=Config.VECTOR_DB_PATH,
        embedding_model=Config.EMBEDDING_MODEL
    )
    
    retriever = RAGRetriever(vector_store, Config.OPENAI_API_KEY)
    
    test_questions = [
        "What time are Sunday services?",
        "What is The Door's mission?",
        "How can I get involved?",
        "Who are the leaders at The Door?"
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        result = retriever.answer_question(question)
        print(f"A: {result['answer']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Sources: {len(result['sources'])} documents")