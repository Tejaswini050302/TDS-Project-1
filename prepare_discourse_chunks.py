import os
import json
import textwrap

INPUT_FILE = "discourse_posts.json"
OUTPUT_FILE = "discourse_chunks.json"
MAX_CHARS = 1000  # You can tune this based on the average chunk size you want

def chunk_text(text, max_chars):
    return textwrap.wrap(text, max_chars, break_long_words=False, break_on_hyphens=False)

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    chunks = []
    for post in posts:
        content = post["content"].strip()
        if not content:
            continue

        pieces = chunk_text(content, MAX_CHARS)
        for i, chunk in enumerate(pieces):
            chunks.append({
                "source": "discourse",
                "topic_id": post["topic_id"],
                "post_id": post["post_id"],
                "chunk_id": f"{post['post_id']}_{i}",
                "text": chunk,
                "metadata": {
                    "author": post["author"],
                    "created_at": post["created_at"],
                    "reply_count": post["reply_count"],
                    "like_count": post["like_count"],
                    "url": post["url"],
                    "is_accepted_answer": post["is_accepted_answer"],
                    "topic_title": post["topic_title"]
                }
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print("Saved:", OUTPUT_FILE)

if __name__ == "__main__":
    main()
