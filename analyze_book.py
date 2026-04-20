import docx
import json
import urllib.request
import time

def call_openai(text_chunk):
    with open('/data/.openclaw/agents/main/agent/auth-profiles.json') as f:
        auth = json.load(f)
    key = auth['profiles']['openai:default']['key']
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    
    system_prompt = (
        'Du bist ein strenger Buchlektor für das Sachbuch "Das 0-Euro-Cockpit". Analysiere den folgenden Abschnitt '
        'auf: 1) Rechtschreib-, Tipp- und Grammatikfehler, 2) Holprige oder unklare Formulierungen. '
        'Mache pro Fehler einen Aufzählungspunkt mit dem Fehler, Originalsatz in Anführungszeichen, und '
        'dem Verbesserungsvorschlag. Wenn der Abschnitt einwandfrei ist, antworte exakt mit "Keine nennenswerten Fehler".'
    )
    
    data = {
        'model': 'gpt-4o-mini',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text_chunk}
        ],
        'temperature': 0.1
    }
    
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())['choices'][0]['message']['content']
                return result
        except Exception as e:
            print(f"API Error: {e}")
            time.sleep(2)
    return "Fehler bei der API-Abfrage."

print("Lese Dokument ein...")
doc = docx.Document('/data/.openclaw/workspace/MITCH/0 Euro Cockpit.docx')
paras = [p.text for p in doc.paragraphs if p.text.strip()]

chunks = []
current_chunk = []
current_words = 0

for p in paras:
    words = len(p.split())
    if current_words + words > 1000:
        chunks.append('\n'.join(current_chunk))
        current_chunk = [p]
        current_words = words
    else:
        current_chunk.append(p)
        current_words += words
if current_chunk:
    chunks.append('\n'.join(current_chunk))

total_chunks = len(chunks)
print(f"Starte Analyse von {total_chunks} Textabschnitten...")

with open('/data/.openclaw/workspace/MITCH/0_Euro_Cockpit_Analyse.md', 'w', encoding='utf-8') as f:
    f.write("# Lektorats-Analyse: Das 0-Euro-Cockpit\n\n")

for i, chunk in enumerate(chunks):
    res = call_openai(chunk)
    with open('/data/.openclaw/workspace/MITCH/0_Euro_Cockpit_Analyse.md', 'a', encoding='utf-8') as f:
        f.write(f"## Abschnitt {i+1} von {total_chunks}\n\n{res}\n\n---\n\n")
    print(f"Abschnitt {i+1}/{total_chunks} analysiert.")

print("Analyse abgeschlossen!")
