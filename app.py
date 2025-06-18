from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import typesense
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the TDS Virtual TA API. Use GET or POST /api/ to ask questions."}

# Define request model for POST
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

# Setup TypeSense client
client = typesense.Client({
    "api_key": os.getenv("TYPESENSE_API_KEY"),
    "nodes": [{
        "host": os.getenv("TYPESENSE_HOST"),
        "port": int(os.getenv("TYPESENSE_PORT")),
        "protocol": os.getenv("TYPESENSE_PROTOCOL")
    }],
    "connection_timeout_seconds": 5
})

# Search TypeSense
def search_typesense(query_text: str, top_k: int = 5):
    results = client.collections["tds_chunks"].documents.search({
        "q": query_text,
        "query_by": "text",
        "num_typos": 2,
        "per_page": top_k
    })
    return results["hits"]

# Query GPT via AI Proxy
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

# ✅ POST endpoint
@app.post("/api/")
async def ask_post(query: QueryRequest):
    hits = search_typesense(query.question)
    contexts = [hit["document"]["text"] for hit in hits]
    sources = [hit["document"]["source"] for hit in hits]
    answer = generate_answer(query.question, contexts)
    return {
        "answer": answer,
        "links": [{"url": src, "text": "Relevant link"} for src in sources]
    }

# ✅ GET endpoint
@app.get("/api/")
async def ask_get(question: str = Query(...)):
    hits = search_typesense(question)
    contexts = [hit["document"]["text"] for hit in hits]
    sources = [hit["document"]["source"] for hit in hits]
    answer = generate_answer(question, contexts)
    return {
        "answer": answer,
        "links": [{"url": src, "text": "Relevant link"} for src in sources]
    }
