import json
import requests
import time

INPUT_FILE = "all_chunks.json"
OUTPUT_FILE = "embedded_chunks.json"
AIPROXY_TOKEN="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjIwMDQ3MThAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.PiG5xHpZWHojap_efGEONx0xcW1eLTsaWBlgtxZLlL8"
EMBEDDING_URL = "https://aiproxy.sanand.workers.dev/openai/v1/embeddings"

HEADERS = {
    "Authorization": f"Bearer {AIPROXY_TOKEN}",
    "Content-Type": "application/json"
}

MODEL = "text-embedding-3-small"

def embed_text(text):
    data = {
        "model": MODEL,
        "input": [text]
    }
    response = requests.post(EMBEDDING_URL, headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    embedded = []
    for i, chunk in enumerate(chunks):
        try:
            emb = embed_text(chunk["text"])
            chunk["embedding"] = emb
            embedded.append(chunk)

            if i % 25 == 0:
                print(f"Embedded {i}/{len(chunks)}")

            time.sleep(1.2)  # Respect AI Proxy rate limits
        except Exception as e:
            print(f"Error at index {i}: {e}")
            continue

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(embedded, f, indent=2)

    print(f"Saved {len(embedded)} embeddings to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
