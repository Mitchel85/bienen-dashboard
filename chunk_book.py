import docx
import json

doc = docx.Document("/data/.openclaw/workspace/MITCH/0 Euro Cockpit.docx")
paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

chunks = []
current_chunk = []
current_words = 0
MAX_WORDS = 800

for p in paragraphs:
    words = len(p.split())
    if current_words + words > MAX_WORDS and current_chunk:
        chunks.append("\n\n".join(current_chunk))
        # Keep the last paragraph as overlap
        current_chunk = [current_chunk[-1], p]
        current_words = len(current_chunk[0].split()) + words
    else:
        current_chunk.append(p)
        current_words += words

if current_chunk:
    chunks.append("\n\n".join(current_chunk))

state = {
    "total_chunks": len(chunks),
    "chunks": chunks,
    "completed": {},
    "current_target_language": "English"
}

with open("/data/.openclaw/workspace/translation_state.json", "w") as f:
    json.dump(state, f, indent=2)

print(f"Book split into {len(chunks)} chunks.")
