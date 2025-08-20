import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
import os
from typing import List, Dict, Set

class WebsiteScraper:
    def __init__(self, base_url: str, output_dir: str):
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict] = []
        
    def is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return (parsed.netloc == urlparse(self.base_url).netloc and
                not any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.css', '.js']))
    
    def extract_text_content(self, soup: BeautifulSoup) -> str:
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return '\n'.join(chunk for chunk in chunks if chunk)
    
    def scrape_page(self, url: str) -> Dict:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.title.string if soup.title else url
            content = self.extract_text_content(soup)
            
            links = []
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if self.is_valid_url(full_url):
                    links.append(full_url)
            
            # Debug: show some found links
            if links:
                print(f"   Sample links found: {links[:3]}...")
            else:
                print("   No valid links found on this page")
            
            return {
                'url': url,
                'title': title.strip(),
                'content': content,
                'links': list(set(links)),
                'scraped_at': time.time()
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def crawl_website(self, max_pages: int = 50, delay: float = 2.0):
        urls_to_visit = [self.base_url]
        
        print(f"🚀 Starting crawl with max_pages={max_pages}, delay={delay}s")
        
        while urls_to_visit and len(self.scraped_data) < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                print(f"⏭️  Already visited: {current_url}")
                continue
                
            print(f"🕷️  Scraping ({len(self.scraped_data)+1}/{max_pages}): {current_url}")
            page_data = self.scrape_page(current_url)
            
            if page_data:
                self.scraped_data.append(page_data)
                self.visited_urls.add(current_url)
                
                print(f"✅ Success! Found {len(page_data['links'])} links")
                print(f"📄 Content length: {len(page_data['content'])} characters")
                
                # Add found links to queue
                new_links = 0
                for link in page_data['links']:
                    if link not in self.visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)
                        new_links += 1
                
                print(f"🔗 Added {new_links} new URLs to queue")
                print(f"📋 Queue size: {len(urls_to_visit)}")
            else:
                print(f"❌ Failed to scrape: {current_url}")
            
            if delay > 0:
                print(f"⏸️  Waiting {delay}s before next request...")
                time.sleep(delay)
        
        print(f"\n📊 Crawling completed:")
        print(f"   Pages scraped: {len(self.scraped_data)}")
        print(f"   Pages visited: {len(self.visited_urls)}")
        print(f"   URLs remaining: {len(urls_to_visit)}")
    
    def save_data(self):
        os.makedirs(self.output_dir, exist_ok=True)
        
        with open(os.path.join(self.output_dir, 'scraped_pages.json'), 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        for i, page in enumerate(self.scraped_data):
            filename = f"page_{i:03d}_{urlparse(page['url']).path.replace('/', '_')}.txt"
            with open(os.path.join(self.output_dir, filename), 'w', encoding='utf-8') as f:
                f.write(f"Title: {page['title']}\n")
                f.write(f"URL: {page['url']}\n")
                f.write(f"Content:\n{page['content']}")
        
        print(f"Saved {len(self.scraped_data)} pages to {self.output_dir}")

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config.config import Config
    
    scraper = WebsiteScraper(Config.BASE_URL, Config.RAW_DATA_PATH)
    scraper.crawl_website(max_pages=30)
    scraper.save_data()