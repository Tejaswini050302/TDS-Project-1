import os
import json
import re

COURSE_DIR = "course"
OUTPUT_FILE = "course_chunks.json"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

def extract_text_from_md(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove YAML frontmatter
    content = re.sub(r"---.*?---", "", content, flags=re.DOTALL)
    return content.strip()

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk = " ".join(words[i:i + size])
        chunks.append(chunk)
    return chunks

def main():
    all_chunks = []

    for filename in os.listdir(COURSE_DIR):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(COURSE_DIR, filename)
        raw_text = extract_text_from_md(filepath)
        chunks = chunk_text(raw_text)

        for chunk in chunks:
            all_chunks.append({
                "source": filename,
                "text": chunk
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"Saved: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
