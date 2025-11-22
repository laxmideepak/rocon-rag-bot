import json
import os
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import faiss
import numpy as np
import requests
from openai import OpenAI
from collections import defaultdict

from config import OPENAI_API_KEY, EMBED_MODEL, BASE_DIR

client = OpenAI(api_key=OPENAI_API_KEY)

# Use absolute paths based on project root
DOCS_PATH = BASE_DIR / "data" / "docs.jsonl"
VS_DIR = BASE_DIR / "vectorstore"
INDEX_PATH = VS_DIR / "faiss_index.bin"
META_PATH = VS_DIR / "metadata.pkl"


def load_docs() -> List[Dict]:
    """Load pre-chunked documents from JSONL."""
    docs = []
    docs_path = str(DOCS_PATH)
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"Documents file not found: {docs_path}")
    with open(docs_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))
    return docs


def build_faiss_index():
    """Build FAISS index from pre-chunked documents."""
    docs = load_docs()
    
    if not docs:
        raise ValueError(f"No documents found in {DOCS_PATH}")
    
    print(f"📚 Loaded {len(docs)} chunks from {DOCS_PATH}")
    
    # Extract content and metadata
    chunks = []
    metadata = []
    
    for idx, doc in enumerate(docs):
        content = doc.get("content", "")
        if not content or len(content.strip()) < 20:
            continue
        
        chunks.append(content)
        metadata.append({
            "doc_idx": idx,
            "url": doc.get("url", ""),
            "title": doc.get("title", ""),
            "category": doc.get("category", ""),
            "heading": doc.get("heading", ""),
            "section_level": doc.get("section_level", 0),
            "chunk_id": doc.get("chunk_id", ""),
            "chunk_index": doc.get("chunk_index", 0),
            "word_count": doc.get("word_count", 0),
        })
    
    print(f"✅ Processing {len(chunks)} valid chunks")
    
    # Generate embeddings in batches
    BATCH_SIZE = 64
    embeddings = []
    
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        print(f"⏳ Embedding batch {i//BATCH_SIZE + 1}/{(len(chunks)-1)//BATCH_SIZE + 1}")
        
        try:
            resp = client.embeddings.create(
                model=EMBED_MODEL,
                input=batch
            )
            batch_embeddings = [e.embedding for e in resp.data]
            embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"❌ Error embedding batch {i//BATCH_SIZE + 1}: {e}")
            raise
    
    # Convert to numpy array
    X = np.array(embeddings, dtype="float32")
    print(f"📊 Embedding matrix shape: {X.shape}")
    
    # Normalize for cosine similarity (using Inner Product)
    faiss.normalize_L2(X)
    
    # Build FAISS index
    dim = X.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner Product = cosine similarity when normalized
    index.add(X)
    
    print(f"✅ FAISS index created with {index.ntotal} vectors")
    
    # Save index and metadata
    vs_dir = str(VS_DIR)
    os.makedirs(vs_dir, exist_ok=True)
    index_path = str(INDEX_PATH)
    meta_path = str(META_PATH)
    
    faiss.write_index(index, index_path)
    
    with open(meta_path, "wb") as f:
        pickle.dump({
            "metadata": metadata,
            "chunks": chunks
        }, f)
    
    print(f"💾 Index saved to {INDEX_PATH}")
    print(f"💾 Metadata saved to {META_PATH}")
    
    # Print statistics
    print_index_stats(metadata)


def print_index_stats(metadata: List[Dict]):
    """Print statistics about the indexed documents."""
    categories = defaultdict(int)
    urls = set()
    
    for m in metadata:
        categories[m["category"]] += 1
        urls.add(m["url"])
    
    print("\n📊 Index Statistics:")
    print(f"   Total chunks: {len(metadata)}")
    print(f"   Unique pages: {len(urls)}")
    print(f"\n📁 Chunks by category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"      {cat}: {count}")


def download_from_blob(url: str, path: str):
    """Download file from Vercel Blob Storage."""
    if not os.path.exists(path):
        print(f"Downloading {os.path.basename(path)} from blob storage...")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Downloaded {os.path.basename(path)}")
        except Exception as e:
            print(f"❌ Error downloading from blob: {e}")
            raise


def load_index() -> Tuple[faiss.Index, Dict]:
    """Load FAISS index and metadata."""
    # Convert Path objects to strings for file operations
    index_path = str(INDEX_PATH)
    meta_path = str(META_PATH)
    
    # Download from Vercel Blob if URLs are provided and files don't exist
    blob_faiss_url = os.getenv("VERCEL_BLOB_FAISS_URL")
    blob_meta_url = os.getenv("VERCEL_BLOB_META_URL")
    
    if blob_faiss_url and not os.path.exists(index_path):
        download_from_blob(blob_faiss_url, index_path)
    
    if blob_meta_url and not os.path.exists(meta_path):
        download_from_blob(blob_meta_url, meta_path)
    
    # Check if files exist after potential download
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError(
            f"Index not found. Run build_faiss_index() first.\n"
            f"Expected files:\n  - {index_path}\n  - {meta_path}\n"
            f"Current working directory: {os.getcwd()}\n"
            f"BASE_DIR: {BASE_DIR}\n"
            f"Or set VERCEL_BLOB_FAISS_URL and VERCEL_BLOB_META_URL environment variables."
        )
    
    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        payload = pickle.load(f)
    
    return index, payload


def search_similar(
    query: str,
    k: int = 10,
    category_filter: Optional[str] = None,
    rerank: bool = True
) -> List[Dict]:
    """
    Search for similar chunks with optional filtering and reranking.
    
    Args:
        query: Search query
        k: Number of results to return (after reranking if enabled)
        category_filter: Optional category to filter by
        rerank: Whether to rerank results using cross-encoder scoring
    
    Returns:
        List of result dictionaries with content, metadata, and scores
    """
    index, payload = load_index()
    metadata = payload["metadata"]
    chunks = payload["chunks"]
    
    # Embed query
    resp = client.embeddings.create(model=EMBED_MODEL, input=[query])
    qvec = np.array(resp.data[0].embedding, dtype="float32").reshape(1, -1)
    faiss.normalize_L2(qvec)
    
    # Initial retrieval: get more candidates for reranking
    initial_k = k * 3 if rerank else k
    scores, indices = index.search(qvec, min(initial_k, index.ntotal))
    
    # Build initial results
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:  # FAISS returns -1 for missing results
            continue
        
        meta = metadata[idx]
        chunk = chunks[idx]
        
        # Apply category filter
        if category_filter and meta["category"] != category_filter:
            continue
        
        results.append({
            **meta,
            "vector_score": float(score),
            "content": chunk,
        })
    
    # Rerank using simple relevance scoring
    if rerank and len(results) > 0:
        results = rerank_results(query, results)
    
    # Return top-k results
    return results[:k]


def rerank_results(query: str, results: List[Dict]) -> List[Dict]:
    """
    Rerank results using hybrid scoring (vector + keyword + metadata).
    
    This provides better relevance than vector search alone.
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    for result in results:
        content_lower = result["content"].lower()
        heading_lower = result["heading"].lower()
        title_lower = result["title"].lower()
        
        # 1. Vector similarity score (already normalized 0-1)
        vector_score = result["vector_score"]
        
        # 2. Keyword overlap score in content
        content_words = set(content_lower.split())
        keyword_score = len(query_words & content_words) / max(len(query_words), 1)
        
        # 3. Heading/title relevance boost
        heading_boost = 0.0
        if any(word in heading_lower for word in query_words):
            heading_boost = 0.2
        if any(word in title_lower for word in query_words):
            heading_boost += 0.1
        
        # 4. Section level boost (prefer top-level sections)
        level_boost = max(0, (4 - result["section_level"])) * 0.02
        
        # Combined score (weighted)
        final_score = (
            vector_score * 0.6 +          # 60% vector similarity
            keyword_score * 0.25 +        # 25% keyword match
            heading_boost +                # Up to 30% heading relevance
            level_boost                    # Up to 6% for section importance
        )
        
        result["rerank_score"] = final_score
        result["keyword_score"] = keyword_score
    
    # Sort by reranked score
    results.sort(key=lambda x: x["rerank_score"], reverse=True)
    return results


def search_with_context(
    query: str,
    k: int = 5,
    expand_context: bool = True
) -> List[Dict]:
    """
    Search with automatic context expansion.
    
    When a chunk is retrieved, also includes adjacent chunks from the same document
    to provide better context continuity.
    """
    # Get initial results
    results = search_similar(query, k=k, rerank=True)
    
    if not expand_context or not results:
        return results
    
    # Load full payload for context expansion
    _, payload = load_index()
    metadata = payload["metadata"]
    chunks = payload["chunks"]
    
    # Group chunks by URL and chunk_index
    url_chunks = defaultdict(list)
    for idx, meta in enumerate(metadata):
        url_chunks[meta["url"]].append((meta.get("chunk_index", 0), idx, meta, chunks[idx]))
    
    # Expand context for each result
    expanded_results = []
    seen_urls = set()
    
    for result in results:
        url = result["url"]
        
        # Avoid duplicate URLs in results
        if url in seen_urls:
            continue
        seen_urls.add(url)
        
        # Get adjacent chunks
        current_chunk_idx = result.get("chunk_index", 0)
        url_chunk_list = sorted(url_chunks[url])
        
        # Find current position
        context_chunks = []
        for chunk_idx, idx, meta, content in url_chunk_list:
            # Include current chunk and immediate neighbors
            if abs(chunk_idx - current_chunk_idx) <= 1:
                context_chunks.append(content)
        
        # Combine context
        if len(context_chunks) > 1:
            result["content_with_context"] = "\n\n---\n\n".join(context_chunks)
        else:
            result["content_with_context"] = result["content"]
        
        expanded_results.append(result)
    
    return expanded_results


def search_by_category(category: str, limit: int = 20) -> List[Dict]:
    """Get all chunks from a specific category."""
    _, payload = load_index()
    metadata = payload["metadata"]
    chunks = payload["chunks"]
    
    results = []
    for idx, meta in enumerate(metadata):
        if meta["category"] == category:
            results.append({
                **meta,
                "content": chunks[idx]
            })
    
    return results[:limit]


if __name__ == "__main__":
    # Build the index
    build_faiss_index()
    
    # Test search
    print("\n" + "="*50)
    print("Testing search functionality")
    print("="*50)
    
    test_query = "How do I create a new site?"
    print(f"\n🔍 Query: {test_query}")
    
    results = search_similar(test_query, k=3, rerank=True)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result['title']}")
        print(f"Category: {result['category']}")
        print(f"Heading: {result['heading']}")
        print(f"URL: {result['url']}")
        print(f"Vector Score: {result['vector_score']:.4f}")
        print(f"Rerank Score: {result.get('rerank_score', 0):.4f}")
        print(f"Content preview: {result['content'][:200]}...")
