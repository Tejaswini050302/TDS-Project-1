from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import typesense
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# TypeSense client
client = typesense.Client({
    "api_key": os.getenv("TYPESENSE_API_KEY"),
    "nodes": [{
        "host": os.getenv("TYPESENSE_HOST"),
        "port": int(os.getenv("TYPESENSE_PORT")),
        "protocol": os.getenv("TYPESENSE_PROTOCOL"),
    }],
    "connection_timeout_seconds": 5
})

class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

def search_typesense(query_text: str, top_k: int = 5):
    results = client.collections["tds_chunks"].documents.search({
        "q": query_text,
        "query_by": "text",
        "num_typos": 2,
        "per_page": top_k
    })
    return results["hits"]

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
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    resp = requests.post(
        os.getenv("OPENAI_API_BASE") + "v1/chat/completions",
        json=payload,
        headers=headers
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def get_links(hits):
    return [{"url": hit["document"].get("source", "#"), "text": "Related content"} for hit in hits]

@app.post("/api/")
async def ask_post(req: QueryRequest):
    hits = search_typesense(req.question)
    contexts = [h["document"]["text"] for h in hits]
    links = get_links(hits)
    answer = generate_answer(req.question, contexts)
    return {"answer": answer, "links": links}

@app.get("/api/")
async def ask_get(question: str = Query(...)):
    hits = search_typesense(question)
    contexts = [h["document"]["text"] for h in hits]
    links = get_links(hits)
    answer = generate_answer(question, contexts)
    return {"answer": answer, "links": links}

@app.get("/")
def root():
    return {"message": "Welcome to the TDS Virtual TA API. Use GET or POST /api/ to ask questions."}
