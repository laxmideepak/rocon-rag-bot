import os
import time
import urllib.parse as up
import urllib.robotparser as rp
from collections import deque
from typing import Set, Dict, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from config import DOCS_BASE_URL, RAW_HTML_DIR

# Crawler Configuration
USER_AGENT = "ROCONDocsBot/1.0 (+https://github.com/yourorg/rocon-docs-bot)"
CRAWL_DELAY = 2.0  # Seconds between requests (respectful rate limiting)
TIMEOUT = 15  # Request timeout in seconds
MAX_RETRIES = 3  # Retry failed requests
RETRY_DELAY = 5  # Seconds between retries


class DocumentationCrawler:
    """Ethical web crawler for ROCON documentation with robots.txt compliance."""
    
    def __init__(self, base_url: str, max_pages: int = 200):
        self.base_url = base_url.rstrip("/")
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        
        # Crawl state
        self.seen_urls: Set[str] = set()
        self.failed_urls: Dict[str, str] = {}
        self.stats = {
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "duplicate": 0
        }
        
        # Setup robots.txt parser
        self.robot_parser = rp.RobotFileParser()
        self.setup_robots_txt()
        
        # Create output directory
        os.makedirs(RAW_HTML_DIR, exist_ok=True)
    
    def setup_robots_txt(self):
        """Check and parse robots.txt for compliance."""
        robots_url = f"{self.base_url}/robots.txt"
        print(f"📋 Checking robots.txt at {robots_url}")
        
        try:
            self.robot_parser.set_url(robots_url)
            self.robot_parser.read()
            
            # Check if we can crawl
            if not self.robot_parser.can_fetch(USER_AGENT, self.base_url):
                print(f"⚠️  WARNING: robots.txt disallows crawling {self.base_url}")
                print("   Proceeding anyway (internal docs) but review robots.txt")
            else:
                print("✅ robots.txt allows crawling")
            
            # Check for crawl delay
            crawl_delay = self.robot_parser.crawl_delay(USER_AGENT)
            if crawl_delay:
                print(f"⏱️  robots.txt specifies crawl-delay: {crawl_delay}s")
                global CRAWL_DELAY
                CRAWL_DELAY = max(CRAWL_DELAY, crawl_delay)
        
        except Exception as e:
            print(f"⚠️  Could not fetch robots.txt: {e}")
            print("   Proceeding with default crawl rate")
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL to avoid duplicates."""
        # Remove fragment
        url = url.split("#")[0]
        
        # Remove trailing slash
        if url.endswith("/") and url != self.base_url + "/":
            url = url[:-1]
        
        # Remove common query parameters that don't change content
        parsed = up.urlparse(url)
        if parsed.query:
            # Keep only essential query params (if any)
            # For documentation, usually we want to remove all query params
            url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        return url
    
    def is_in_scope(self, url: str) -> bool:
        """Check if URL is within crawl scope."""
        return url.startswith(self.base_url)
    
    def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched per robots.txt."""
        try:
            return self.robot_parser.can_fetch(USER_AGENT, url)
        except:
            return True  # If check fails, proceed with caution
    
    def url_to_filename(self, url: str) -> str:
        """Convert URL to safe filename."""
        # Remove protocol
        fname = url.replace("https://", "").replace("http://", "")
        # Replace slashes with underscores
        fname = fname.replace("/", "_")
        # Remove unsafe characters
        fname = "".join(c for c in fname if c.isalnum() or c in "._-")
        return f"{fname}.html"
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with retries and error handling."""
        for attempt in range(MAX_RETRIES):
            try:
                resp = self.session.get(url, timeout=TIMEOUT)
                
                # Check status code
                if resp.status_code == 404:
                    print(f"   ⚠️  404 Not Found: {url}")
                    self.failed_urls[url] = "404 Not Found"
                    return None
                
                if resp.status_code != 200:
                    print(f"   ⚠️  Status {resp.status_code}: {url}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    self.failed_urls[url] = f"Status {resp.status_code}"
                    return None
                
                # Check content type
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    print(f"   ℹ️  Skipping non-HTML: {content_type}")
                    self.stats["skipped"] += 1
                    return None
                
                return resp.text
            
            except requests.exceptions.Timeout:
                print(f"   ⏱️  Timeout (attempt {attempt + 1}/{MAX_RETRIES}): {url}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    self.failed_urls[url] = "Timeout"
            
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request error: {e}")
                self.failed_urls[url] = str(e)
                return None
        
        return None
    
    def extract_links(self, html: str, base_url: str) -> Set[str]:
        """Extract and normalize all links from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            
            # Skip mailto, javascript, etc.
            if href.startswith(("mailto:", "javascript:", "tel:", "#")):
                continue
            
            # Convert relative URLs to absolute
            absolute_url = up.urljoin(base_url + "/", href)
            
            # Normalize and check scope
            normalized = self.normalize_url(absolute_url)
            if self.is_in_scope(normalized):
                links.add(normalized)
        
        return links
    
    def save_html(self, url: str, html: str):
        """Save HTML content to file."""
        filename = self.url_to_filename(url)
        filepath = os.path.join(RAW_HTML_DIR, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8", errors="ignore") as f:
                f.write(html)
            return True
        except Exception as e:
            print(f"   ❌ Error saving {filename}: {e}")
            return False
    
    def crawl(self):
        """Main crawl loop."""
        print("\n" + "="*60)
        print("🕷️  ROCON Documentation Crawler")
        print("="*60)
        print(f"Base URL: {self.base_url}")
        print(f"Max Pages: {self.max_pages}")
        print(f"Crawl Delay: {CRAWL_DELAY}s")
        print(f"Output Dir: {RAW_HTML_DIR}")
        print("="*60 + "\n")
        
        # Initialize queue
        queue = deque([self.base_url])
        
        # Progress bar
        pbar = tqdm(total=self.max_pages, desc="📄 Crawling pages", unit="page")
        
        start_time = time.time()
        
        while queue and len(self.seen_urls) < self.max_pages:
            url = queue.popleft()
            url = self.normalize_url(url)
            
            # Skip if already seen
            if url in self.seen_urls:
                self.stats["duplicate"] += 1
                continue
            
            # Check robots.txt
            if not self.can_fetch(url):
                print(f"⛔ Blocked by robots.txt: {url}")
                self.stats["skipped"] += 1
                continue
            
            # Mark as seen
            self.seen_urls.add(url)
            
            # Fetch page
            html = self.fetch_page(url)
            
            if html:
                # Save HTML
                if self.save_html(url, html):
                    self.stats["success"] += 1
                    pbar.update(1)
                    pbar.set_postfix({
                        "success": self.stats["success"],
                        "failed": self.stats["failed"],
                        "queue": len(queue)
                    })
                else:
                    self.stats["failed"] += 1
                
                # Extract and queue new links
                links = self.extract_links(html, url)
                for link in links:
                    if link not in self.seen_urls:
                        queue.append(link)
            else:
                self.stats["failed"] += 1
            
            # Respectful rate limiting
            time.sleep(CRAWL_DELAY)
        
        pbar.close()
        
        # Print summary
        elapsed = time.time() - start_time
        self.print_summary(elapsed)
        
        return self.stats
    
    def print_summary(self, elapsed: float):
        """Print crawl summary statistics."""
        print("\n" + "="*60)
        print("📊 Crawl Summary")
        print("="*60)
        print(f"✅ Successfully crawled: {self.stats['success']} pages")
        print(f"❌ Failed: {self.stats['failed']} pages")
        print(f"⏭️  Skipped: {self.stats['skipped']} pages")
        print(f"🔄 Duplicates avoided: {self.stats['duplicate']}")
        print(f"⏱️  Total time: {elapsed:.1f}s")
        print(f"⚡ Average rate: {self.stats['success'] / elapsed:.2f} pages/sec")
        
        if self.failed_urls:
            print(f"\n❌ Failed URLs ({len(self.failed_urls)}):")
            for url, reason in list(self.failed_urls.items())[:10]:
                print(f"   {url}: {reason}")
            if len(self.failed_urls) > 10:
                print(f"   ... and {len(self.failed_urls) - 10} more")
        
        print("="*60 + "\n")


def crawl_docs(max_pages: int = 200):
    """Convenience function to crawl documentation."""
    crawler = DocumentationCrawler(
        base_url=DOCS_BASE_URL,
        max_pages=max_pages
    )
    return crawler.crawl()


if __name__ == "__main__":
    # Crawl with reasonable limit
    crawl_docs(max_pages=400)
