import json
import docx
import os

WORKSPACE = "/data/.openclaw/workspace"
STATE_FILE = os.path.join(WORKSPACE, "translation_state.json")
OUTPUT_DOCX = os.path.join(WORKSPACE, "MITCH", "0_Euro_Cockpit_English.docx")

with open(STATE_FILE, "r", encoding="utf-8") as f:
    state = json.load(f)

completed = state.get("completed", {})
total = state.get("total_chunks", 26)

doc = docx.Document()

for i in range(total):
    chunk_text = completed.get(str(i), "")
    paragraphs = chunk_text.split('\n\n')
    for p in paragraphs:
        if p.strip():
            doc.add_paragraph(p.strip())

doc.save(OUTPUT_DOCX)
print(f"Saved DOCX to {OUTPUT_DOCX}")
