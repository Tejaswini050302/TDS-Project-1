# TDS Virtual TA Project 1

This is a **Virtual Teaching Assistant** for the **Tools in Data Science (TDS)** course in the IIT Madras Online BS Data Science program. It can answer student questions using **Retrieval-Augmented Generation (RAG)** with course content and Discourse forum posts as knowledge sources.

> Built for the **Virtual TA** project submission 

---

 **Live URL**: [https://tds-va-project-1.onrender.com](https://tds-va-project-1.onrender.com)

# 🧪 Try It Out
You can use:

[Hoppscotch](https://hoppscotch.io/) or Postman to send requests to https://tds-va-project-1.onrender.com/ask

---


## Project Goals

Create a working API that:

- Accepts a **question** (and optional base64 image)
- Searches both **course content** and **Discourse posts**
- Uses OpenAI's `gpt-4o-mini` (via AI Proxy) to generate a concise answer
- Returns:
  - A final answer (string)
  - A list of source links used

---

## 🗂️ Project Structure

tds/
├── app.py # Main FastAPI application
├── .env # API keys and config (not pushed to GitHub)
├── embedded_chunks.json # Combined course + forum data with embeddings
├── index_to_typesense.py # Indexes embedded chunks into TypeSense
├── generate_embeddings.py # Generates embeddings using AI Proxy
├── prepare_course_chunks.py # Parses Markdown course pages into chunks
├── prepare_discourse_chunks.py# Parses forum JSON files into chunks
├── discourse/ # Folder with scraped Discourse JSON files
├── tds_pages_md/ # Folder with Markdown pages from TDS site
├── requirements.txt # Python dependencies
└── README.md # This file

---

## ⚙️ Tech Stack

- **FastAPI** – Web framework for building APIs  
- **TypeSense** – Vector search engine  
- **OpenAI via AI Proxy** – GPT-4o-mini for generating answers  
- **Playwright** – For scraping content  
- **Markdownify** – Converts HTML content to Markdown  
- **Requests** – Handles API calls  

---

## 🚀 How It Works

1. The user sends a POST request with a question (and optionally an image).
2. TypeSense searches for the most relevant chunks from the course + forum.
3. GPT-4o-mini generates a concise answer using only those chunks.
4. The API responds with the answer and source metadata.

---

## 🧩 Components & Workflow

### 1. 🕸 Scrape Data  
- `website_downloader_full.py`: Downloads the TDS course content into `.md` files from the course site.  
- `discourse_downloader_single.py`: Logs into the IITM Discourse forum and saves each topic post as individual JSON files.

### 2. ✂️ Chunk Data  
- `prepare_course_chunks.py`: Splits the Markdown course content into smaller chunks for embedding.  
- `prepare_discourse_chunks.py`: Splits Discourse forum data into clean, usable text chunks.  
- `combine_chunks.py`: Merges the course and forum chunks into a single dataset.

### 3. 🧠 Embed & Index  
- `generate_embeddings.py`: Creates vector embeddings using `text-embedding-3-small` via the AI Proxy.  
- `index_to_typesense.py`: Uploads the chunks and embeddings to a TypeSense vector database hosted on a cluster or `localhost:8001`.

### 4. ⚙️ Serve API  
- `app.py`: FastAPI backend exposing a `/ask` endpoint that performs search + GPT-4o-mini answer generation using context from the database.

---

## Example API Call

```bash
curl -X POST "https://tds-va-project-1.onrender.com/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt-3.5-turbo?",
    "image": null
  }'
```
---
## Setup Locally (optional)
Clone your project repo:
```
git clone https://github.com/your-username/your-repo.git
cd your-repo
```
Create a .env file:
```
OPENAI_API_KEY=your-token
OPENAI_API_BASE=https://aiproxy.sanand.workers.dev/openai/
OPENAI_MODEL=gpt-4o-mini
EMBED_MODEL=text-embedding-3-small

TYPESENSE_HOST=your-cluster.typesense.net
TYPESENSE_PORT=443
TYPESENSE_PROTOCOL=https
TYPESENSE_API_KEY=your-typesense-key
```
-Install dependencies:
```
pip install -r requirements.txt
```
-Run the API:
```
uvicorn app:app --host 0.0.0.0 --port 10000
```
---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
