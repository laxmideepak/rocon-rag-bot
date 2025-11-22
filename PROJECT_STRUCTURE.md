# ROCON RAG Bot - Project Structure

## Current Structure (Vercel-Ready)

```
rocon-rag-bot/
├── api/                          # Vercel serverless functions
│   ├── chat.py                  # Main API endpoint for Vercel
│   └── requirements.txt         # Python dependencies for Vercel
│
├── app/                          # Application code
│   ├── __init__.py
│   ├── chat.py                  # RAG chat logic
│   ├── config.py                # Configuration
│   ├── crawl_docs.py            # Web crawler
│   ├── ingest.py                # Document ingestion
│   ├── vectorstore.py           # FAISS vector store
│   ├── main.py                  # Local FastAPI app
│   ├── test_rag_system.py       # Test suite
│   └── debug_ingest.py          # Debug tools
│
├── data/                         # Data files
│   ├── docs.jsonl               # Processed documents (needed for Vercel)
│   └── raw_html/                # Raw HTML files (excluded from Vercel)
│
├── vectorstore/                  # Vector store files (needed for Vercel)
│   ├── faiss_index.bin          # FAISS index
│   └── metadata.pkl              # Metadata
│
├── .env                          # Environment variables (NOT in git)
├── .gitignore                    # Git ignore rules
├── .vercelignore                 # Vercel ignore rules
├── vercel.json                   # Vercel configuration
├── requirements.txt              # Local development dependencies
├── README.md                     # Project documentation
├── DEPLOYMENT.md                 # Deployment guide
└── DEPLOY_CHECKLIST.md          # Deployment checklist
```

## Vercel Deployment Structure

### Key Files for Vercel:
- ✅ `api/chat.py` - Serverless function entry point
- ✅ `api/requirements.txt` - Vercel Python dependencies
- ✅ `vercel.json` - Vercel configuration
- ✅ `app/` - Application modules (imported by api/chat.py)
- ✅ `data/docs.jsonl` - Processed documents
- ✅ `vectorstore/` - FAISS index files

### Excluded from Vercel:
- ❌ `data/raw_html/` - Large HTML files (excluded via .vercelignore)
- ❌ `.env` - Environment variables (set in Vercel dashboard)
- ❌ `__pycache__/` - Python cache files
- ❌ Test and debug files

## Local Development

Run locally with:
```bash
uvicorn app.main:app --reload --port 8000
```

## Vercel Deployment

Deploy with:
```bash
vercel --prod
```

