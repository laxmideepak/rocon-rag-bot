# api/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found")

DOCS_BASE_URL = os.getenv("DOCS_BASE_URL", "https://docs.roconpaas.io/")

# Models
EMBED_MODEL = "text-embedding-3-large"
CHAT_MODEL = "gpt-4o-mini"  # Fixed from gpt-4.1-mini

# Paths - CRITICAL: Use absolute paths for Vercel
BASE_DIR = Path("/tmp")  # Vercel uses /tmp for runtime files
DOCS_JSONL = BASE_DIR / "docs.jsonl"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
FAISS_INDEX_BIN = VECTORSTORE_DIR / "faiss_index.bin"
FAISS_INDEX_PKL = VECTORSTORE_DIR / "metadata.pkl"

# Parameters
TEMPERATURE = 0.1
TOP_K_RESULTS = 6
CHUNK_SIZE = 512
CHUNK_OVERLAP = 102
