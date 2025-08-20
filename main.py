#!/usr/bin/env python3
import os
import sys
import argparse
import json

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from src.scraper.playwright_scraper import PlaywrightScraper
from src.embeddings.text_processor import TextProcessor
from src.embeddings.vector_store import VectorStore

def scrape_website():
    print("🕷️  Scraping The Door website with Playwright...")
    
    try:
        scraper = PlaywrightScraper(Config.BASE_URL, Config.RAW_DATA_PATH)
        scraper.crawl_website(max_pages=15, delay_range=(2, 4))
        
        # Check if we got reasonable results
        if len(scraper.scraped_data) >= 3:
            scraper.save_data()
            print("✅ Playwright scraping completed successfully!")
            return True
        else:
            print(f"⚠️  Only scraped {len(scraper.scraped_data)} pages - using fallback")
            from src.scraper.simple_scraper import create_sample_data
            create_sample_data(Config.RAW_DATA_PATH)
            print("✅ Sample data created!")
            return False
            
    except Exception as e:
        print(f"❌ Playwright scraping failed: {e}")
        print("📝 Using comprehensive sample data instead...")
        from src.scraper.simple_scraper import create_sample_data
        create_sample_data(Config.RAW_DATA_PATH)
        print("✅ Sample data created!")
        return False

def process_documents():
    print("📄 Processing documents...")
    processor = TextProcessor(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    
    scraped_data_path = os.path.join(Config.RAW_DATA_PATH, 'scraped_pages.json')
    processed_data_path = os.path.join(Config.PROCESSED_DATA_PATH, 'processed_chunks.json')
    
    if not os.path.exists(scraped_data_path):
        print(f"❌ Scraped data not found at {scraped_data_path}")
        print("Please run scraping first: python main.py --scrape")
        return False
    
    chunks = processor.process_scraped_data(scraped_data_path)
    processor.save_processed_data(chunks, processed_data_path)
    print("✅ Document processing completed!")
    return True

def create_embeddings():
    print("🔢 Creating embeddings and populating vector store...")
    
    processed_data_path = os.path.join(Config.PROCESSED_DATA_PATH, 'processed_chunks.json')
    
    if not os.path.exists(processed_data_path):
        print(f"❌ Processed data not found at {processed_data_path}")
        print("Please run processing first: python main.py --process")
        return False
    
    vector_store = VectorStore(
        db_path=Config.VECTOR_DB_PATH,
        embedding_model=Config.EMBEDDING_MODEL
    )
    
    with open(processed_data_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    vector_store.add_documents(chunks)
    stats = vector_store.get_collection_stats()
    print(f"✅ Vector store created! Stats: {stats}")
    return True

def run_chatbot():
    print("🤖 Starting chatbot...")
    os.system("streamlit run src/chatbot/app.py")

def setup_pipeline():
    print("🚀 Running complete RAG pipeline setup...")
    
    if not scrape_website():
        return False
    
    if not process_documents():
        return False
        
    if not create_embeddings():
        return False
    
    print("✅ RAG pipeline setup completed successfully!")
    print("🤖 You can now run the chatbot with: python main.py --chatbot")
    return True

def main():
    parser = argparse.ArgumentParser(description="The Door RAG Chatbot Pipeline")
    parser.add_argument("--scrape", action="store_true", help="Scrape the website")
    parser.add_argument("--process", action="store_true", help="Process scraped documents")
    parser.add_argument("--embeddings", action="store_true", help="Create embeddings")
    parser.add_argument("--chatbot", action="store_true", help="Run the chatbot")
    parser.add_argument("--setup", action="store_true", help="Run complete setup pipeline")
    
    args = parser.parse_args()
    
    if not any([args.scrape, args.process, args.embeddings, args.chatbot, args.setup]):
        print("📋 The Door RAG Chatbot")
        print("\nAvailable commands:")
        print("  --setup      Run complete pipeline setup")
        print("  --scrape     Scrape The Door website")
        print("  --process    Process scraped documents")
        print("  --embeddings Create embeddings")
        print("  --chatbot    Run the chatbot interface")
        print("\nFor first-time setup, use: python main.py --setup")
        return
    
    if args.setup:
        setup_pipeline()
    elif args.scrape:
        scrape_website()
    elif args.process:
        process_documents()
    elif args.embeddings:
        create_embeddings()
    elif args.chatbot:
        run_chatbot()

if __name__ == "__main__":
    main()