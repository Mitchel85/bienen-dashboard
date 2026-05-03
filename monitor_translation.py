import json
import time
import os

WORKSPACE = "/data/.openclaw/workspace"
STATE_FILE = os.path.join(WORKSPACE, "translation_state.json")

print("Monitoring translation progress...")

while True:
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        completed = len(state.get("completed", {}))
        total = state.get("total_chunks", 26)
        
        if completed >= total:
            print("Translation finished. Triggering DOCX generation.")
            # We will handle DOCX generation after
            break
        time.sleep(30)
    except Exception as e:
        time.sleep(30)
