import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

DOCS_BASE_URL = os.getenv("DOCS_BASE_URL", "https://docs.roconpaas.io/")

# Model Configuration
# Embedding model: text-embedding-3-large for better accuracy
# Alternative: text-embedding-3-small for lower cost (62.3% vs 64.6% MTEB)
EMBED_MODEL = "text-embedding-3-large"

# Chat model: gpt-4o-mini (NOT gpt-4.1-mini which doesn't exist!)
# This is OpenAI's fast, affordable model for focused tasks
CHAT_MODEL = "gpt-4o-mini"

# Alternative chat models for different use cases:
# - "gpt-4o" - More powerful but more expensive
# - "gpt-4-turbo" - Good balance of power and cost
# - "o4-mini" - For reasoning-heavy tasks (more expensive)

# LLM Parameters
TEMPERATURE = 0.1  # Lower for more focused answers (was 0.7)
TOP_K_RESULTS = 6  # Number of chunks to retrieve (was 5)

# Chunking Configuration (optimized for documentation RAG)
CHUNK_SIZE = 512  # tokens (~400 words) - optimal for doc search
CHUNK_OVERLAP = 102  # 20% overlap for context preservation
MAX_CHUNK_SIZE = 800  # Maximum tokens per chunk
MIN_CHUNK_SIZE = 100  # Minimum tokens per chunk

# Path Configuration
BASE_DIR = Path(__file__).parent.parent
RAW_HTML_DIR = BASE_DIR / "data" / "raw_html"
DOCS_JSONL = BASE_DIR / "data" / "docs.jsonl"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
FAISS_INDEX_BIN = VECTORSTORE_DIR / "faiss_index.bin"
FAISS_INDEX_PKL = VECTORSTORE_DIR / "metadata.pkl"  # Renamed for clarity

# Retrieval Configuration
RETRIEVAL_TOP_K = 10  # Initial retrieval before reranking
RERANK_TOP_K = 6  # Final number after reranking
USE_QUERY_EXPANSION = True  # Enable LLM-based query expansion
USE_RERANKING = True  # Enable hybrid reranking

# Search Configuration
VECTOR_WEIGHT = 0.6  # Weight for vector similarity in reranking
KEYWORD_WEIGHT = 0.25  # Weight for keyword matching
METADATA_WEIGHT = 0.15  # Weight for metadata signals

# Context Configuration
EXPAND_CONTEXT = True  # Include adjacent chunks from same document
CONTEXT_WINDOW = 1  # Number of adjacent chunks to include (each side)

# Embedding Batch Configuration
EMBEDDING_BATCH_SIZE = 64  # Batch size for embedding generation
MAX_RETRIES = 3  # Maximum retries for API calls
RETRY_DELAY = 2  # Seconds to wait between retries

# Model costs (per 1M tokens) - for tracking/budgeting
COSTS = {
    "text-embedding-3-small": 0.00002,
    "text-embedding-3-large": 0.00013,
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "o4-mini": {"input": 1.10, "output": 4.40},
}

# Backward compatibility aliases
EMBEDDING_MODEL = EMBED_MODEL
LLM_MODEL = CHAT_MODEL

# Feature Flags
ENABLE_LOGGING = True
ENABLE_CACHING = False  # Future: implement response caching
ENABLE_ANALYTICS = False  # Future: track query patterns


# Validation
def validate_config():
    """Validate configuration settings."""
    issues = []
    
    if not OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY is required")
    
    if CHAT_MODEL not in ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "o4-mini"]:
        issues.append(f"Invalid CHAT_MODEL: {CHAT_MODEL}")
    
    if EMBED_MODEL not in ["text-embedding-3-small", "text-embedding-3-large"]:
        issues.append(f"Invalid EMBED_MODEL: {EMBED_MODEL}")
    
    if CHUNK_OVERLAP >= CHUNK_SIZE:
        issues.append(f"CHUNK_OVERLAP ({CHUNK_OVERLAP}) must be less than CHUNK_SIZE ({CHUNK_SIZE})")
    
    if issues:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {i}" for i in issues))
    
    return True


# Run validation on import
validate_config()


# Print configuration summary
if __name__ == "__main__":
    print("="*60)
    print("ROCON RAG Bot Configuration")
    print("="*60)
    print(f"\n🤖 Models:")
    print(f"   Chat Model: {CHAT_MODEL}")
    print(f"   Embedding Model: {EMBED_MODEL}")
    print(f"\n📊 Chunking:")
    print(f"   Chunk Size: {CHUNK_SIZE} tokens")
    print(f"   Chunk Overlap: {CHUNK_OVERLAP} tokens ({CHUNK_OVERLAP/CHUNK_SIZE*100:.0f}%)")
    print(f"\n🔍 Retrieval:")
    print(f"   Top K (initial): {RETRIEVAL_TOP_K}")
    print(f"   Top K (final): {RERANK_TOP_K}")
    print(f"   Query Expansion: {USE_QUERY_EXPANSION}")
    print(f"   Reranking: {USE_RERANKING}")
    print(f"\n💰 Estimated Costs (per 1M tokens):")
    print(f"   Embeddings: ${COSTS[EMBED_MODEL]:.5f}")
    print(f"   Chat Input: ${COSTS[CHAT_MODEL]['input']:.2f}")
    print(f"   Chat Output: ${COSTS[CHAT_MODEL]['output']:.2f}")
    print(f"\n📁 Paths:")
    print(f"   HTML Source: {RAW_HTML_DIR}")
    print(f"   Docs JSONL: {DOCS_JSONL}")
    print(f"   Vector Store: {VECTORSTORE_DIR}")
    print("\n" + "="*60)
