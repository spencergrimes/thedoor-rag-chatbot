import json
import os
import time
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Page, Browser
import random

class PlaywrightScraper:
    def __init__(self, base_url: str, output_dir: str):
        self.base_url = base_url
        self.output_dir = output_dir
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict] = []
        self.browser = None
        self.page = None
        
    def is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return (parsed.netloc == urlparse(self.base_url).netloc and
                not any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.css', '.js', '#', 'mailto:', 'tel:']))
    
    def extract_text_content(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script, style, nav, footer, header elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return '\n'.join(chunk for chunk in chunks if chunk)
    
    def setup_browser(self):
        """Initialize Playwright browser with realistic settings"""
        print("🚀 Starting browser...")
        self.playwright = sync_playwright().start()
        
        # Use Chromium with realistic user agent and settings
        self.browser = self.playwright.chromium.launch(
            headless=True,  # Set to False to see browser for debugging
            args=[
                '--no-sandbox',
                '--disable-bgsync',
                '--disable-extensions-file-access-check',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-sync'
            ]
        )
        
        # Create context with realistic browser settings
        context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/Chicago'
        )
        
        self.page = context.new_page()
        
        # Set reasonable timeouts
        self.page.set_default_timeout(30000)  # 30 seconds
        self.page.set_default_navigation_timeout(30000)
        
    def cleanup_browser(self):
        """Clean up browser resources"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def scrape_page(self, url: str) -> Dict:
        try:
            print(f"   🌐 Loading page...")
            
            # Navigate to page
            response = self.page.goto(url, wait_until='networkidle')
            
            if not response or response.status >= 400:
                print(f"   ❌ HTTP {response.status if response else 'No response'}")
                return None
            
            # Wait for page to fully load
            self.page.wait_for_load_state('networkidle')
            time.sleep(random.uniform(1, 3))  # Random delay to seem human
            
            # Get page content
            html = self.page.content()
            title = self.page.title() or url
            
            # Extract clean text content
            content = self.extract_text_content(html)
            
            # Find links
            links = []
            link_elements = self.page.query_selector_all('a[href]')
            
            for element in link_elements:
                href = element.get_attribute('href')
                if href:
                    full_url = urljoin(url, href)
                    if self.is_valid_url(full_url):
                        links.append(full_url)
            
            # Remove duplicates
            links = list(set(links))
            
            print(f"   ✅ Success! Content: {len(content)} chars, Links: {len(links)}")
            
            return {
                'url': url,
                'title': title.strip(),
                'content': content,
                'links': links,
                'scraped_at': time.time()
            }
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None
    
    def crawl_website(self, max_pages: int = 50, delay_range: tuple = (2, 5)):
        urls_to_visit = [self.base_url]
        
        print(f"🚀 Starting Playwright crawl (max_pages={max_pages})")
        
        try:
            self.setup_browser()
            
            while urls_to_visit and len(self.scraped_data) < max_pages:
                current_url = urls_to_visit.pop(0)
                
                if current_url in self.visited_urls:
                    continue
                
                print(f"🕷️  Scraping ({len(self.scraped_data)+1}/{max_pages}): {current_url}")
                
                page_data = self.scrape_page(current_url)
                
                if page_data:
                    self.scraped_data.append(page_data)
                    self.visited_urls.add(current_url)
                    
                    # Add new links to queue
                    new_links = 0
                    for link in page_data['links']:
                        if link not in self.visited_urls and link not in urls_to_visit:
                            urls_to_visit.append(link)
                            new_links += 1
                    
                    print(f"   📝 Added {new_links} new URLs (queue: {len(urls_to_visit)})")
                
                # Human-like random delay
                if len(urls_to_visit) > 0:
                    delay = random.uniform(*delay_range)
                    print(f"   ⏸️  Waiting {delay:.1f}s...")
                    time.sleep(delay)
            
        finally:
            self.cleanup_browser()
        
        print(f"\n📊 Crawling completed:")
        print(f"   ✅ Pages scraped: {len(self.scraped_data)}")
        print(f"   📋 URLs visited: {len(self.visited_urls)}")
        print(f"   ⏭️  URLs remaining: {len(urls_to_visit)}")
    
    def save_data(self):
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save as JSON
        json_path = os.path.join(self.output_dir, 'scraped_pages.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        # Save individual text files
        for i, page in enumerate(self.scraped_data):
            path_part = urlparse(page['url']).path.replace('/', '_') or 'home'
            filename = f"page_{i:03d}_{path_part}.txt"
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Title: {page['title']}\n")
                f.write(f"URL: {page['url']}\n")
                f.write(f"Content:\n{page['content']}")
        
        print(f"💾 Saved {len(self.scraped_data)} pages to {self.output_dir}")

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from config.config import Config
    
    scraper = PlaywrightScraper(Config.BASE_URL, Config.RAW_DATA_PATH)
    scraper.crawl_website(max_pages=15, delay_range=(2, 4))
    scraper.save_data()