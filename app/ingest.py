import json
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
import hashlib
from typing import List, Dict, Optional

RAW_DIR = "data/raw_html"
OUT_PATH = "data/docs.jsonl"

# Optimal chunking parameters based on 2025 best practices
CHUNK_SIZE = 512  # tokens (roughly 400 words)
CHUNK_OVERLAP = 102  # 20% overlap for context preservation


def extract_structured_content(html: str, url: str) -> Optional[Dict]:
    """Extract content while preserving document structure and hierarchy."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Find main content area
    # Based on debug analysis, ROCON docs use betterdocs-entry-content
    main = (
        soup.find("div", class_="betterdocs-entry-content") or
        soup.find("article") or
        soup.find("div", class_="entry-content") or
        soup.find("div", class_="betterdocs-content-area") or
        soup.find("main") or
        soup.body
    )
    
    if not main:
        return None
    
    # Remove noise elements
    for selector in ["header", "footer", "nav", "aside", "script", "style", 
                     ".sidebar", "#sidebar", ".navigation", ".breadcrumb"]:
        for tag in main.select(selector):
            tag.decompose()
    
    # Extract page title with better fallback
    page_title = None
    title_tag = soup.find("title")
    if title_tag:
        page_title = title_tag.get_text(strip=True)
        # Clean common patterns like "Page Title - Site Name"
        if " - " in page_title:
            page_title = page_title.split(" - ")[0].strip()
        if " | " in page_title:
            page_title = page_title.split(" | ")[0].strip()
    
    # Extract structured sections with hierarchy
    sections = []
    current_section = {"heading": page_title or "Introduction", "level": 1, "content": []}
    
    for element in main.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'li', 'pre', 'code', 'table']):
        if element.name in ['h1', 'h2', 'h3', 'h4']:
            # Save previous section if it has content
            if current_section["content"]:
                sections.append(current_section.copy())
            
            # Start new section
            heading_text = element.get_text(strip=True)
            level = int(element.name[1])
            current_section = {"heading": heading_text, "level": level, "content": []}
        
        else:
            # Extract text content (avoid duplicates by only getting direct text)
            if element.name == 'li':
                text = element.get_text(separator=" ", strip=True)
                if text and text not in current_section["content"]:
                    current_section["content"].append(f"• {text}")
            elif element.name in ['pre', 'code']:
                text = element.get_text(strip=True)
                if text:
                    current_section["content"].append(f"``````")
            elif element.name == 'table':
                # Preserve table structure
                text = extract_table_text(element)
                if text:
                    current_section["content"].append(text)
            else:  # paragraph
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Filter out very short fragments
                    current_section["content"].append(text)
    
    # Add final section
    if current_section["content"]:
        sections.append(current_section)
    
    return {
        "title": page_title or "Untitled",
        "sections": sections,
        "url": url
    }


def extract_table_text(table_element) -> str:
    """Extract table content in a readable format."""
    rows = []
    for row in table_element.find_all('tr'):
        cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
        if cells:
            rows.append(" | ".join(cells))
    return "\n".join(rows) if rows else ""


def create_chunks(sections: List[Dict], base_metadata: Dict) -> List[Dict]:
    """Create semantically meaningful chunks with overlap."""
    chunks = []
    
    for section in sections:
        heading = section["heading"]
        level = section["level"]
        content_parts = section["content"]
        
        if not content_parts:
            continue
        
        # Combine content with heading
        full_text = f"# {heading}\n\n" + "\n\n".join(content_parts)
        
        # Simple word-based chunking (you can replace with tiktoken for precise token count)
        words = full_text.split()
        
        if len(words) <= CHUNK_SIZE:
            # Section fits in one chunk
            chunks.append({
                **base_metadata,
                "heading": heading,
                "section_level": level,
                "content": full_text,
                "chunk_id": generate_chunk_id(full_text),
                "word_count": len(words)
            })
        else:
            # Split into multiple overlapping chunks
            start = 0
            chunk_index = 0
            while start < len(words):
                end = start + CHUNK_SIZE
                chunk_words = words[start:end]
                chunk_text = " ".join(chunk_words)
                
                # Prepend heading to each chunk for context
                if chunk_index > 0:
                    chunk_text = f"# {heading} (continued)\n\n{chunk_text}"
                else:
                    chunk_text = f"# {heading}\n\n{chunk_text}"
                
                chunks.append({
                    **base_metadata,
                    "heading": heading,
                    "section_level": level,
                    "content": chunk_text,
                    "chunk_id": generate_chunk_id(chunk_text),
                    "chunk_index": chunk_index,
                    "word_count": len(chunk_words)
                })
                
                # Move forward with overlap
                start = end - CHUNK_OVERLAP
                chunk_index += 1
    
    return chunks


def generate_chunk_id(text: str) -> str:
    """Generate unique ID for deduplication."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:16]


def infer_category_from_url(url: str) -> str:
    """Infer category from URL path for better metadata."""
    url_lower = url.lower()
    
    if "account-configuration" in url_lower or "billing" in url_lower:
        return "Account Configuration"
    elif "organization" in url_lower:
        return "Organizations"
    elif "blueprint" in url_lower:
        return "Blueprints"
    elif "manage" in url_lower or "website" in url_lower:
        return "Website Management"
    elif "support" in url_lower or "ticket" in url_lower:
        return "Support"
    elif "user-role" in url_lower or "privilige" in url_lower:
        return "User Management"
    elif "getting-started" in url_lower or "home" in url_lower:
        return "Getting Started"
    else:
        return "General Documentation"


def build_docs_jsonl():
    """Main ingestion pipeline with proper chunking and metadata."""
    all_chunks = []
    seen_chunk_ids = set()  # Deduplication
    
    html_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".html")]
    
    for fname in tqdm(html_files, desc="Processing documentation"):
        path = os.path.join(RAW_DIR, fname)
        
        # Reconstruct URL from filename
        url = "https://docs.roconpaas.io/" + fname.replace("_", "/").replace(".html", "")
        
        with open(path, encoding="utf-8", errors='ignore') as f:
            html = f.read()
        
        # Extract structured content
        doc_data = extract_structured_content(html, url)
        if not doc_data or not doc_data["sections"]:
            print(f"⚠️  Skipped {fname}: No content extracted")
            continue
        
        # Infer category
        category = infer_category_from_url(url)
        
        # Create base metadata
        base_metadata = {
            "url": url,
            "title": doc_data["title"],
            "category": category,
            "source_file": fname
        }
        
        # Create chunks with overlap
        doc_chunks = create_chunks(doc_data["sections"], base_metadata)
        
        # Deduplicate chunks
        for chunk in doc_chunks:
            chunk_id = chunk["chunk_id"]
            if chunk_id not in seen_chunk_ids:
                all_chunks.append(chunk)
                seen_chunk_ids.add(chunk_id)
    
    # Write to JSONL
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    
    print(f"\n✅ Successfully processed {len(html_files)} HTML files")
    print(f"✅ Created {len(all_chunks)} chunks")
    print(f"✅ Output saved to: {OUT_PATH}")
    
    # Print statistics
    categories = {}
    for chunk in all_chunks:
        cat = chunk["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Chunks by category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count} chunks")


if __name__ == "__main__":
    build_docs_jsonl()
