from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import typesense
import requests
import os
from dotenv import load_dotenv
import traceback

# Load .env variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# TypeSense client
client = typesense.Client({
    "api_key": os.getenv("TYPESENSE_API_KEY"),
    "nodes": [{
        "host": os.getenv("TYPESENSE_HOST"),
        "port": int(os.getenv("TYPESENSE_PORT")),
        "protocol": os.getenv("TYPESENSE_PROTOCOL")
    }],
    "connection_timeout_seconds": 5
})

# Request format
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None  # Can be extended later

# Search TypeSense
def search_typesense(query_text: str, top_k: int = 5):
    results = client.collections["tds_chunks"].documents.search({
        "q": query_text,
        "query_by": "text",
        "num_typos": 2,
        "per_page": top_k
    })
    return results["hits"]

# Ask GPT via AI Proxy
def generate_answer(question: str, contexts: List[str]):
    context_block = "\n\n".join(contexts)
    system_msg = "You are a helpful assistant for the IIT Madras TDS course. Use only the context provided."

    payload = {
        "model": os.getenv("OPENAI_MODEL"),  # gpt-4o-mini
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{context_block}"}
        ]
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        os.getenv("OPENAI_API_BASE") + "v1/chat/completions",
        json=payload,
        headers=headers
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Main endpoint
@app.post("/ask")
async def ask_question(query: QueryRequest):
    try:
        hits = search_typesense(query.question)

        if not hits:
            return {
                "question": query.question,
                "answer": "Sorry, I couldn't find any relevant information.",
                "sources": []
            }

        contexts = [hit["document"]["text"] for hit in hits]
        sources = [hit["document"]["source"] for hit in hits]
        answer = generate_answer(query.question, contexts)

        return {
            "question": query.question,
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
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

