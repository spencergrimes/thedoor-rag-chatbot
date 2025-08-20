import json
import os
from typing import List, Dict, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np

class VectorStore:
    def __init__(self, db_path: str, embedding_model: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.embedding_model_name = embedding_model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        os.makedirs(db_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name="thedoor_documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
    
    def add_documents(self, chunks: List[Dict]):
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.generate_embeddings(texts)
        
        ids = [chunk['id'] for chunk in chunks]
        metadatas = [{
            'source_url': chunk['source_url'],
            'source_title': chunk['source_title'],
            'chunk_index': chunk['chunk_index'],
            'token_count': chunk['token_count']
        } for chunk in chunks]
        
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(chunks)} documents to vector store")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        query_embedding = self.generate_embeddings([query])[0]
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        search_results = []
        for i in range(len(results['documents'][0])):
            search_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity_score': 1 - results['distances'][0][i]
            })
        
        return search_results
    
    def get_collection_stats(self) -> Dict:
        count = self.collection.count()
        return {
            'total_documents': count,
            'embedding_model': self.embedding_model_name
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
    
    processed_data_path = os.path.join(Config.PROCESSED_DATA_PATH, 'processed_chunks.json')
    
    if os.path.exists(processed_data_path):
        with open(processed_data_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        vector_store.add_documents(chunks)
        stats = vector_store.get_collection_stats()
        print(f"Vector store stats: {stats}")
    else:
        print(f"Processed data not found at {processed_data_path}")