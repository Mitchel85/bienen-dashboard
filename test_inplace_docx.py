import json, docx
import os

WORKSPACE = "/data/.openclaw/workspace"
ORIGINAL_DOCX = os.path.join(WORKSPACE, "MITCH", "0 Euro Cockpit.docx")
STATE_FILE = os.path.join(WORKSPACE, "translation_state.json")
OUTPUT_DOCX = os.path.join(WORKSPACE, "MITCH", "0_Euro_Cockpit_English_Full_Layout.docx")

# Load translated paragraphs
with open(STATE_FILE, "r", encoding="utf-8") as f:
    state = json.load(f)

trans_paras = []
for i in range(26):
    chunk_text = state["completed"].get(str(i), "")
    c_paras = [p.strip() for p in chunk_text.split("\n\n") if p.strip()]
    if i > 0 and len(c_paras) > 0:
        c_paras = c_paras[1:] # Drop overlap
    trans_paras.extend(c_paras)

print(f"Loaded {len(trans_paras)} translated paragraphs.")

doc = docx.Document(ORIGINAL_DOCX)
t_idx = 0
replaced = 0

for p in doc.paragraphs:
    if p.text.strip():
        # This paragraph has text.
        if t_idx < len(trans_paras):
            # To preserve formatting as much as possible, we might just clear the text
            # and append the new text, but setting p.text = ... clears all runs.
            # If the paragraph ONLY contains text, this is fine.
            # If it contains an inline image AND text, the image might be lost.
            p.text = trans_paras[t_idx]
            replaced += 1
            t_idx += 1

doc.save(OUTPUT_DOCX)
print(f"Replaced {replaced} paragraphs. Saved to {OUTPUT_DOCX}.")
