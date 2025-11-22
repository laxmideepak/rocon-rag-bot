from fastapi import FastAPI
from pydantic import BaseModel

from .chat import answer_question

app = FastAPI(title="Rocon RAG Chatbot")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = answer_question(req.message)
    return ChatResponse(**result)


@app.get("/")
def root():
    return {
        "title": "Rocon RAG Chatbot",
        "endpoints": {
            "/chat": "POST - Chat with the RAG bot",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation (Swagger UI)",
        }
    }


@app.get("/health")
def health():
    return {"status": "ok"}
