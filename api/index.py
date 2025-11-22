# api/index.py
"""
Vercel serverless function for RAG chatbot API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from chat import answer_question
from vectorstore import search_similar

# Initialize FastAPI
app = FastAPI(
    title="ROCON Docs API",
    description="RAG-powered documentation chatbot API",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    question: str
    use_query_expansion: Optional[bool] = True
    temperature: Optional[float] = 0.1


class ChatResponse(BaseModel):
    answer: str
    sources: list
    metadata: dict


class SearchRequest(BaseModel):
    query: str
    k: Optional[int] = 5


# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "ROCON Docs RAG API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    try:
        # Check OpenAI API key
        from config import OPENAI_API_KEY
        if not OPENAI_API_KEY:
            return {
                "status": "unhealthy",
                "error": "OPENAI_API_KEY not set in environment variables"
            }
        
        # Quick test that vectorstore is accessible
        from vectorstore import load_index
        index, _ = load_index()
        return {
            "status": "healthy",
            "vectors_indexed": index.ntotal
        }
    except FileNotFoundError as e:
        return {
            "status": "unhealthy",
            "error": f"Vectorstore files not found: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for RAG queries
    """
    try:
        if not request.question or len(request.question.strip()) < 3:
            raise HTTPException(status_code=400, detail="Question too short")
        
        # Get answer from RAG system
        result = answer_question(
            request.question,
            use_query_expansion=request.use_query_expansion,
            temperature=request.temperature
        )
        
        return ChatResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/api/search")
async def search(request: SearchRequest):
    """
    Direct vector search endpoint (faster, no LLM)
    """
    try:
        results = search_similar(request.query, k=request.k)
        return {
            "query": request.query,
            "results": results[:request.k]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
