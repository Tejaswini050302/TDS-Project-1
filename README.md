# 🤖 TDS Virtual TA Project 1

This is a **Virtual Teaching Assistant** for the **Tools in Data Science (TDS)** course in the IIT Madras Online BS Data Science program. It can answer student questions using **Retrieval-Augmented Generation (RAG)** with course content and Discourse forum posts as knowledge sources.

> Built for the **Virtual TA** project submission 

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

## 🧱 Components & Workflow

1. **Scrape Data**  
   - `website_downloader_full.py`: downloads the course content into `.md` files
   - `discourse_downloader_single.py`: logs into IITM Discourse and saves post JSON files

2. **Chunk Data**  
   - `prepare_course_chunks.py`: splits course Markdown into chunks
   - `prepare_discourse_chunks.py`: splits Discourse JSON into chunks
   - `combine_chunks.py`: merges all into one file

3. **Embed & Index**  
   - `generate_embeddings.py`: creates embeddings using `text-embedding-3-small` via AI Proxy
   - `index_to_typesense.py`: pushes data + vectors into local TypeSense server (`localhost:8001`)

4. **Serve API**  
   - `main.py`: FastAPI backend for answering questions via `/api/` endpoint

---

## Example API Call

```bash
curl "https://your-api-url.com/api/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
    "image": "<base64-string>"
  }'
```
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
