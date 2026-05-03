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

orig_doc = docx.Document(ORIGINAL_DOCX)
orig_paras_with_text = [p for p in orig_doc.paragraphs if p.text.strip()]

new_doc = docx.Document()

# We need to copy styles carefully, because standard python-docx might crash if a custom style isn't in the new blank doc.
# To avoid custom style crashes, we'll try to apply the style's name. If it fails, fallback to Normal.
for i, t_text in enumerate(trans_paras):
    if i < len(orig_paras_with_text):
        o_style_name = orig_paras_with_text[i].style.name
    else:
        o_style_name = "Normal"
        
    p = new_doc.add_paragraph(t_text)
    try:
        p.style = o_style_name
    except KeyError:
        # Custom styles might not exist in the new default document.
        # Fallback to standard ones if possible, e.g. "Heading 1"
        if "Heading" in o_style_name:
            try:
                p.style = o_style_name
            except:
                pass

new_doc.save(OUTPUT_DOCX)
print("Saved cleanly.")
