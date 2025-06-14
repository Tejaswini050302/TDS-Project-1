# TDS Virtual TA Project 1

This is a **Virtual Teaching Assistant** for the **Tools in Data Science (TDS)** course in the IIT Madras Online BS Data Science program. It can answer student questions using **Retrieval-Augmented Generation (RAG)** with course content and Discourse forum posts as knowledge sources.

> Built for the **Virtual TA** project submission 

---

 **Live URL**: [https://tds-va-project-1.onrender.com](https://tds-va-project-1.onrender.com)

#🧪 Try It Out
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

## 📡 Example API Call

```bash
curl -X POST "https://tds-va-project-1.onrender.com/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt-3.5-turbo?",
    "image": null
  }'
```
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
