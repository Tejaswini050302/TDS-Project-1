from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import typesense
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Typesense client config
client = typesense.Client({
    "api_key": os.getenv("TYPESENSE_API_KEY"),
    "nodes": [{
        "host": os.getenv("TYPESENSE_HOST"),
        "port": int(os.getenv("TYPESENSE_PORT")),
        "protocol": os.getenv("TYPESENSE_PROTOCOL")
    }],
    "connection_timeout_seconds": 5
})

# Pydantic model for POST API
class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

# Search function
def search_typesense(query_text: str, top_k: int = 5):
    results = client.collections["tds_chunks"].documents.search({
        "q": query_text,
        "query_by": "text",
        "num_typos": 2,
        "per_page": top_k
    })
    return results["hits"]

# AI Proxy API
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

# Home page form (GET)
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Handle form submit (POST)
@app.post("/", response_class=HTMLResponse)
async def handle_form(request: Request, question: str = Form(...)):
    hits = search_typesense(question)
    contexts = [hit["document"]["text"] for hit in hits]
    sources = [hit["document"]["source"] for hit in hits]
    answer = generate_answer(question, contexts)

    links = [{"url": src, "text": "View source"} for src in sources]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "answer": answer,
        "links": links
    })

# JSON API endpoint
@app.post("/", response_class=HTMLResponse)
@app.post("/api/")
async def ask_json(query: QueryRequest):
    hits = search_typesense(query.question)
    contexts = [hit["document"]["text"] for hit in hits]
    sources = [hit["document"]["source"] for hit in hits]
    answer = generate_answer(query.question, contexts)
    links = [{"url": src, "text": "View source"} for src in sources]
    return {
        "answer": answer,
        "links": links
    }
