import os
import json
import typesense
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TYPESENSE_API_KEY = os.getenv("TYPESENSE_API_KEY")
TYPESENSE_HOST = os.getenv("TYPESENSE_HOST", "localhost")
TYPESENSE_PORT = int(os.getenv("TYPESENSE_PORT", 8001))
TYPESENSE_PROTOCOL = os.getenv("TYPESENSE_PROTOCOL", "http")

# Initialize Typesense client
client = typesense.Client({
    "api_key": TYPESENSE_API_KEY,
    "nodes": [{
        "host": TYPESENSE_HOST,
        "port": TYPESENSE_PORT,
        "protocol": TYPESENSE_PROTOCOL
    }],
    "connection_timeout_seconds": 10
})

# Define collection schema
schema = {
    "name": "tds_chunks",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "source", "type": "string", "facet": True},
        {"name": "chunk_id", "type": "int32"},
        {"name": "text", "type": "string"},
        {"name": "embedding", "type": "float[]", "num_dim": 1536}
    ],
    "default_sorting_field": "chunk_id"
}

# Delete and create collection
try:
    client.collections["tds_chunks"].delete()
    print("Deleted existing 'tds_chunks' collection")
except Exception:
    print("No existing 'tds_chunks' collection found, creating new one")

client.collections.create(schema)
print("Created collection 'tds_chunks'")

# Index data
with open("embedded_chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

for i, chunk in enumerate(chunks):
    try:
        chunk_id = int(chunk.get("chunk_id", i))  # Force conversion to int
        doc = {
            "id": f"{chunk['source']}_{chunk_id}",
            "source": chunk["source"],
            "chunk_id": chunk_id,
            "text": chunk["text"],
            "embedding": chunk["embedding"]
        }
        client.collections["tds_chunks"].documents.create(doc)
        if i % 25 == 0:
            print(f"Indexed {i}/{len(chunks)}")
    except Exception as e:
        print(f"Error indexing chunk {i}: {e}")

print(f"Finished indexing {len(chunks)} chunks.")
