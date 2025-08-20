import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    BASE_URL = 'https://thedoor.org'
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    VECTOR_DB_PATH = 'data/vectordb'
    RAW_DATA_PATH = 'data/raw'
    PROCESSED_DATA_PATH = 'data/processed'
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    LLM_MODEL = 'gpt-3.5-turbo'
    MAX_TOKENS = 100  # Reduced to save costs