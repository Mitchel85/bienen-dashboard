import json, docx
import os

WORKSPACE = "/data/.openclaw/workspace"
ORIGINAL_DOCX = os.path.join(WORKSPACE, "MITCH", "0 Euro Cockpit.docx")
STATE_FILE = os.path.join(WORKSPACE, "translation_state.json")
OUTPUT_DOCX = os.path.join(WORKSPACE, "MITCH", "0_Euro_Cockpit_English_Formatted.docx")

# Load translated paragraphs
with open(STATE_FILE, "r", encoding="utf-8") as f:
    state = json.load(f)

trans_paras = []
for i in range(26):
    chunk_text = state["completed"][str(i)]
    c_paras = [p.strip() for p in chunk_text.split("\n\n") if p.strip()]
    if i > 0:
        c_paras = c_paras[1:] # Drop overlap
    trans_paras.extend(c_paras)

# Modify original docx
doc = docx.Document(ORIGINAL_DOCX)

t_idx = 0
for p in doc.paragraphs:
    if not p.text.strip():
        # Empty paragraph or just an image. Clear it to remove images!
        p.clear()
    else:
        # Replace text with translation
        if t_idx < len(trans_paras):
            # Keep the style, but replace text
            style = p.style
            p.text = trans_paras[t_idx]
            p.style = style
            t_idx += 1
        else:
            p.clear() # If we run out of translations, clear the rest

# If there are left over translations (e.g. the 1 extra in glossary), just append them
while t_idx < len(trans_paras):
    doc.add_paragraph(trans_paras[t_idx])
    t_idx += 1

doc.save(OUTPUT_DOCX)
print(f"Saved formatted DOCX to {OUTPUT_DOCX}")
