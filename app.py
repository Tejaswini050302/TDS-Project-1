from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional
import typesense
import requests
import os
from dotenv import load_dotenv
from fastapi.openapi.utils import get_openapi

load_dotenv()

app = FastAPI()

# TypeSense configuration
client = typesense.Client({
    "api_key": os.getenv("TYPESENSE_API_KEY"),
    "nodes": [{
        "host": os.getenv("TYPESENSE_HOST"),
        "port": int(os.getenv("TYPESENSE_PORT")),
        "protocol": os.getenv("TYPESENSE_PROTOCOL")
    }],
    "connection_timeout_seconds": 5
})

# Request body model
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

# Search TypeSense for relevant chunks
def search_typesense(query_text: str, top_k: int = 5):
    results = client.collections["tds_chunks"].documents.search({
        "q": query_text,
        "query_by": "text",
        "num_typos": 2,
        "per_page": top_k
    })
    return results["hits"]

# Ask AI Proxy GPT model
def generate_answer(question: str, contexts: List[str]):
    context_block = "\n\n".join(contexts)
    system_msg = "You are a helpful assistant for the IIT Madras TDS course. Use only the context provided."
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{context_block}"}
        ]
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('AIPROXY_TOKEN')}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
        json=payload,
        headers=headers
    )
    return response.json()["choices"][0]["message"]["content"]

# Main API route to answer questions
@app.post("/ask")
async def ask_question(query: QueryRequest):
    hits = search_typesense(query.question)
    contexts = [hit["document"]["text"] for hit in hits]
    sources = [hit["document"]["source"] for hit in hits]
    answer = generate_answer(query.question, contexts)
    return {
        "question": query.question,
        "answer": answer,
        "sources": sources
    }

# Home route to verify deployment
@app.get("/")
def root():
    return {
        "message": "✅ Welcome to the TDS Virtual TA API!",
        "usage": "Send a POST request to /ask with your question. Optional: include a base64 image.",
        "example": {
            "question": "What is the use of hybrid RAG in this course?",
            "image": "<base64-encoded image string (optional)>"
        },
        "docs": "/docs"
    }

# Swagger UI metadata (optional, shows OpenAPI schema)
@app.get("/docs", include_in_schema=False)
def custom_docs():
    return get_openapi(
        title="TDS Virtual TA API",
        version="1.0.0",
        routes=app.routes
    )
