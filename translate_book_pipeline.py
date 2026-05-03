#!/usr/bin/env python3
import json
import subprocess
import os
import time

WORKSPACE = "/data/.openclaw/workspace"
STATE_FILE = os.path.join(WORKSPACE, "translation_state.json")
OUTPUT_FILE = os.path.join(WORKSPACE, "0_Euro_Cockpit_English.md")

with open(STATE_FILE, "r", encoding="utf-8") as f:
    state = json.load(f)

chunks = state["chunks"]
completed = state.get("completed", {})

print(f"Starting translation of {len(chunks)} chunks using Gemini 3.1 Pro Preview...")

for i, chunk in enumerate(chunks):
    chunk_index = str(i)
    if chunk_index in completed:
        print(f"Chunk {i+1}/{len(chunks)} already translated. Skipping.")
        continue
        
    print(f"Translating chunk {i+1}/{len(chunks)}...")
    
    prompt = f"""You are a professional book translator. Translate the following book excerpt (Chunk {i+1} of {len(chunks)}) from the book "Das 0-Euro-Cockpit" from German to English. 
Maintain any line breaks and markdown formatting exactly.
Ensure a fluent, professional, but practical style (like a modern IT guidebook).

TEXT TO TRANSLATE:
{chunk}

REPLY EXCLUSIVELY with the final English translation, no other comments."""

    # Write prompt to temp file
    prompt_file = os.path.join(WORKSPACE, f"temp_prompt_{i}.txt")
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(prompt)
        
    try:
        # Run inference
        cmd = ["openclaw", "infer", "model", "run", "--model", "google/gemini-3.1-pro-preview", "--prompt", prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"Error translating chunk {i+1}: {result.stderr}")
            time.sleep(10)
            continue
            
        output_lines = result.stdout.strip().split("\n")
        
        # Remove the metadata header added by openclaw infer
        if output_lines[0].startswith("model.run via local"):
            output_lines = output_lines[4:]
            
        translated_text = "\n".join(output_lines)
        
        completed[chunk_index] = translated_text
        state["completed"] = completed
        
        # Save state
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
        print(f"Chunk {i+1} completed successfully.")
        
        # Save incremental merged file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
            for j in range(len(chunks)):
                if str(j) in completed:
                    out_f.write(completed[str(j)] + "\n\n")
                    
        time.sleep(2) # Prevent rate limiting
        
    except Exception as e:
        print(f"Exception on chunk {i+1}: {e}")
        time.sleep(10)

print("Pipeline finished.")
