import json
import os
import re
from typing import List, Dict
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-\.\,\!\?\:\;]', '', text)
        return text.strip()
    
    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))
    
    def process_scraped_data(self, scraped_data_path: str) -> List[Dict]:
        with open(scraped_data_path, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        
        processed_chunks = []
        
        for page in scraped_data:
            if not page['content'].strip():
                continue
            
            cleaned_content = self.clean_text(page['content'])
            
            if len(cleaned_content) < 50:
                continue
            
            chunks = self.text_splitter.split_text(cleaned_content)
            
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:
                    continue
                
                chunk_data = {
                    'id': f"{page['url']}_{i}",
                    'source_url': page['url'],
                    'source_title': page['title'],
                    'content': chunk.strip(),
                    'token_count': self.count_tokens(chunk),
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
                processed_chunks.append(chunk_data)
        
        return processed_chunks
    
    def save_processed_data(self, chunks: List[Dict], output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        print(f"Processed {len(chunks)} chunks and saved to {output_path}")
        
        total_tokens = sum(chunk['token_count'] for chunk in chunks)
        avg_tokens = total_tokens / len(chunks) if chunks else 0
        
        print(f"Statistics:")
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Total tokens: {total_tokens}")
        print(f"  Average tokens per chunk: {avg_tokens:.1f}")

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config.config import Config
    
    processor = TextProcessor(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    
    scraped_data_path = os.path.join(Config.RAW_DATA_PATH, 'scraped_pages.json')
    processed_data_path = os.path.join(Config.PROCESSED_DATA_PATH, 'processed_chunks.json')
    
    chunks = processor.process_scraped_data(scraped_data_path)
    processor.save_processed_data(chunks, processed_data_path)