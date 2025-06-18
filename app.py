from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import typesense
import requests
import os
from dotenv import load_dotenv

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

# Request model
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

# GET / route - for homepage or ping
@app.get("/")
def root():
    return {
        "message": "✅ TDS Virtual TA API is live. Send POST requests to /api/"
    }

# Search in TypeSense
def search_typesense(query_text: str, top_k: int = 5):
    results = client.collections["tds_chunks"].documents.search({
        "q": query_text,
        "query_by": "text",
        "num_typos": 2,
        "per_page": top_k
    })
    return results["hits"]

# Call AI Proxy
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

# POST /api
@app.post("/api")
async def ask_question(query: QueryRequest):
    hits = search_typesense(query.question)
    contexts = [hit["document"]["text"] for hit in hits]
    sources = [hit["document"]["source"] for hit in hits]
    answer = generate_answer(query.question, contexts)
    return {
        "answer": answer,
        "links": [{"url": src, "text": "Relevant reference"} for src in sources]
    }
