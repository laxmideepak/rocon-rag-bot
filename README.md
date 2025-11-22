# RAG Bot

A Retrieval-Augmented Generation (RAG) bot for documentation question-answering. This bot crawls documentation websites, processes the content, creates vector embeddings, and provides an intelligent chat interface powered by OpenAI.

## Features

- **Web Crawling**: Automatically crawls documentation websites
- **Document Processing**: Extracts and chunks text from HTML pages
- **Vector Store**: Uses FAISS for efficient similarity search
- **RAG Chat**: Answers questions using retrieved context from documentation
- **FastAPI Interface**: RESTful API for easy integration

## Project Structure

```
rocon-rag-bot/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── crawl_docs.py      # Web crawler
│   ├── ingest.py          # Document processing
│   ├── vectorstore.py     # FAISS vector store
│   ├── chat.py            # RAG chat bot
│   └── main.py            # FastAPI application
├── data/
│   ├── raw_html/          # Downloaded HTML pages
│   └── docs.jsonl         # Processed documents
├── vectorstore/
│   ├── faiss_index.bin    # FAISS index
│   └── faiss_index.pkl    # Document metadata
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── README.md
```

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
   - Copy `.env` and set your `OPENAI_API_KEY`
   - Set `DOCS_BASE_URL` to the documentation website you want to crawl

3. **Crawl documentation**:
```bash
python -m app.crawl_docs
```
Or use the API:
```bash
curl -X POST http://localhost:8000/crawl
```

4. **Process documents**:
```bash
python -m app.ingest
```
Or use the API:
```bash
curl -X POST http://localhost:8000/ingest
```

5. **Build vector store**:
```bash
python -m app.vectorstore build
```
Or use the API:
```bash
curl -X POST http://localhost:8000/build-index
```

## Usage

### Command Line Chat

```bash
python -m app.chat
```

### FastAPI Server

Start the server:
```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /chat` - Chat with the bot
  ```json
  {
    "question": "How do I install the package?",
    "use_rag": true
  }
  ```
- `POST /chat/history` - Chat with conversation history
- `POST /crawl` - Crawl documentation
- `POST /ingest` - Process documents
- `POST /build-index` - Build vector store

### Example API Usage

```bash
# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "use_rag": true}'

# Full pipeline
curl -X POST http://localhost:8000/crawl
curl -X POST http://localhost:8000/ingest
curl -X POST http://localhost:8000/build-index
```

## Configuration

Environment variables in `.env`:

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `DOCS_BASE_URL` - Base URL for documentation to crawl
- `EMBEDDING_MODEL` - Embedding model (default: `text-embedding-3-small`)
- `LLM_MODEL` - Chat model (default: `gpt-4o-mini`)
- `TEMPERATURE` - LLM temperature (default: `0.7`)
- `CHUNK_SIZE` - Text chunk size (default: `1000`)
- `CHUNK_OVERLAP` - Chunk overlap (default: `200`)
- `TOP_K_RESULTS` - Number of results to retrieve (default: `5`)
- `CRAWL_DELAY` - Delay between requests in seconds (default: `1.0`)
- `MAX_PAGES` - Maximum pages to crawl (default: `100`)

## License

MIT

