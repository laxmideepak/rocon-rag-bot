# debug_ingest.py
"""Debug script to identify why ingestion is failing."""

import os
from bs4 import BeautifulSoup
from pathlib import Path

RAW_HTML_DIR = Path("data/raw_html")

def debug_html_parsing():
    """Debug HTML parsing to find the issue."""
    
    print("="*60)
    print("DEBUG: HTML Parsing Analysis")
    print("="*60)
    
    html_files = list(RAW_HTML_DIR.glob("*.html"))
    print(f"\n✅ Found {len(html_files)} HTML files\n")
    
    # Sample 5 files for analysis
    sample_files = html_files[:5]
    
    for i, html_file in enumerate(sample_files, 1):
        print(f"\n{'='*60}")
        print(f"File {i}: {html_file.name}")
        print(f"{'='*60}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        print(f"File size: {len(html)} chars")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        
        # Check what selectors exist
        print("\n🔍 Checking common selectors:")
        
        selectors = [
            ("article", soup.find("article")),
            ("div.entry-content", soup.find("div", class_="entry-content")),
            ("div.betterdocs-content-area", soup.find("div", class_="betterdocs-content-area")),
            ("main", soup.find("main")),
            ("body", soup.find("body")),
        ]
        
        for selector_name, element in selectors:
            if element:
                content = element.get_text(strip=True)
                print(f"  ✅ {selector_name}: Found ({len(content)} chars)")
            else:
                print(f"  ❌ {selector_name}: NOT FOUND")
        
        # Check title
        title_tag = soup.find("title")
        if title_tag:
            print(f"\n📄 Title: {title_tag.get_text(strip=True)}")
        
        # Check for common WordPress/doc classes
        print("\n🔍 Checking for common WordPress/doc elements:")
        wp_classes = [
            "content", "post-content", "entry-content", "article-content",
            "documentation", "docs-content", "page-content"
        ]
        
        for cls in wp_classes:
            elem = soup.find(class_=cls)
            if elem:
                print(f"  ✅ Found class '{cls}'")
        
        # Show first 500 chars of body
        body = soup.find("body")
        if body:
            body_text = body.get_text(strip=True)[:500]
            print(f"\n📝 Body preview (first 500 chars):")
            print(f"   {body_text}...")
        
        # Check all div classes to find the right one
        print(f"\n🔍 All unique div classes in file:")
        all_divs = soup.find_all("div", class_=True)
        unique_classes = set()
        for div in all_divs:
            classes = div.get("class", [])
            unique_classes.update(classes)
        
        for cls in sorted(list(unique_classes))[:20]:  # Show first 20
            print(f"   - {cls}")
        
        if len(unique_classes) > 20:
            print(f"   ... and {len(unique_classes) - 20} more")

if __name__ == "__main__":
    debug_html_parsing()
