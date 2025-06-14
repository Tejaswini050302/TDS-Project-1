import json

course_file = "course_chunks.json"
discourse_file = "discourse_chunks.json"
output_file = "all_chunks.json"

with open(course_file, "r", encoding="utf-8") as f:
    course_chunks = json.load(f)

with open(discourse_file, "r", encoding="utf-8") as f:
    discourse_chunks = json.load(f)

all_chunks = course_chunks + discourse_chunks

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2, ensure_ascii=False)

print(f"Combined {len(course_chunks)} course and {len(discourse_chunks)} discourse chunks.")
print(f"Saved to {output_file}")
