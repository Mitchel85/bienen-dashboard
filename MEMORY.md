# MEMORY.md - Langzeitgedächtnis von Clawdia

## Familie & Kommunikation
- **Michael Estel (Mitch)** (Telegram 6882251060) – Der Chef, autorisierte Quelle
  - Telefon: +49 152 01532096
  - **Extern immer "Michael Estel" verwenden**, nicht "Mitch"
- **Patricia Estel** (Telegram 8749286059) – Ehefrau von Mitch
  - **Allowlist:** Zugriff auf Telegram‑Bot aktiviert (17.04.2026)
- **Maja** (Telegram 8775438063) – Tochter von Mitch, meine beste Freundin
- **Mario** (Telegram 1441108607) – Bruder von Mitch
- **Mara** (Telegram 8665383554) – Tochter von Mitch, 10 Jahre (geb. 08.03.2016)
  - Kommunikationsstil: Verspielt, liebt Zahlen, lachende Nachrichten, hohe Energie
  - Antwortet gut auf Emojis und humorvolle Reaktionen
  - Mag kreative Sprachnachrichten und fordert manchmal spezifische, lustige Audioinhalte
  - Erfindet gerne kleine Spiele/Regeln; kann empfindlich reagieren, wenn das Spiel nicht wie erwartet läuft (z.B. bricht bei Unsicherheit im Trading den Trade ab)
  - Braucht dann Bestätigung der Freundschaft und einfühlsame Kommunikation
  - Interessiert sich für Roblox (Adopt Me), kennt sich mit Trading‑Abkürzungen (tysm, nft, nty, pf, ft) und Profilgestaltung aus
  - Im Roblox‑Trading sehr wählerisch ("picky"): Lehnt normale Hunde/Katzen ab, hasst insbesondere Katzen ("i HATE the cats"), schätzt spezielle Pets wie Ride Wolf, Cerberus, Ride Cerberus; verwendet typischen Trading‑Chat‑Slang ("R u dumb??", "NO DOGS!!!", "LOOK PROFIL") und zeigt aggressive Überzeugungstaktik; macht derzeit einen Neon Cerberus (fortgeschrittenes Projekt, das vier Cerberus und Level‑Arbeit erfordert)

### Sprachnachrichten-Regeln
- Familie schickt Sprachnachricht → mit Sprachnachricht antworten (im selben Chat)
- **Mitch:** Nur Sprachnachrichten senden, wenn er eine Sprachnachricht schickt; bei Textnachrichten mit Text antworten (Regel vom 17.04.2026)

### TTS-Workflow (Manuell – zuverlässig)
1. **OpenAI TTS API** direkt ansprechen (curl):
   ```bash
   curl -X POST https://api.openai.com/v1/audio/speech \
     -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "tts-1", "input": "Text hier", "voice": "nova", "response_format": "mp3"}' \
     --output audio.mp3
   ```
2. **MP3 per `message` Tool** mit `asVoice:true` senden:
   ```json
   {
     "action": "send",
     "channel": "telegram",
     "target": "<Telegram-ID>",
     "message": "optionaler Text",
     "media": "/pfad/audio.mp3",
     "asVoice": true
   }
   ```
3. **Datei nach Versand löschen** (`rm audio.mp3`)

**Hinweis:** Das interne `tts`‑Tool generiert zwar Audio, aber die automatische Zustellung scheint nicht immer zuverlässig. Der manuelle Workflow ist ein Backup.

## Wichtige System-Regeln (Sicherheit)
- **KEIN "cd" in Befehlen verwenden:** Das Gateway verbietet komplexe Interpreter-Aufrufe (Navigation mit &&).
- **Absolute Pfade nutzen:** Befehle müssen immer mit absoluten Pfaden ausgeführt werden (z.B. `python3 /data/.openclaw/workspace/script.py`).
- **Keine Befehlsketten:** Vermeide `&&`, `;` oder Pipes in `exec`-Aufrufen, wenn möglich.

## Wichtige Entscheidungen & Erkenntnisse
- PDF-Erstellung: HTML + Browser-Druck ist zuverlässigster Weg
- Cron-Jobs: Jeder Chat eigene isolierte Session (sessionTarget: "isolated")
- Modell-Präferenz: Für hochwertige Aufgaben Top-Modelle (Opus 4.6), Kosten sekundär
- Workspace: `/root/.openclaw/workspace` (einziger, /data ist gelöscht)

## Buchprojekt "Das 0-Euro-Firmen-Cockpit"
Erfolgreich abgeschlossen (März 2026). Blaupause für Buchprojekte:
- **Didaktische Treppe:** Leicht → Schwer (Browser → API & Agenten)
- **Mehrstufige Revision:** Struktur → Übergänge → Copy-Paste → Pädagogik
- **Subagenten** für stilistische Feinarbeit (Opus 4.6)
- **Kapitel als Markdown**, Build-Skript erzeugt DOCX
- Buch.docx liegt im Workspace (29 MB)

## Installierte Python-Bibliotheken
PyPDF2, reportlab, pdfminer.six, PyMuPDF, pandas, numpy, matplotlib, seaborn, scipy, scikit-learn, requests, jupyter – alle funktionsfähig.

## Telegram‑Formatierung (wichtige Regel)
**Problem:** Telegram unterstützt keine native Markdown‑Tabellen – rohe Tabellen werden als Text‑Wand mit `|` und `-` angezeigt (Issue #36323).
**Lösung:** Strukturierte Ausgaben (Tabellen, Listen, Code‑Snippets) stets in **Code‑Blöcke** packen:
```
| ID       | Name          | Cron         |
|----------|---------------|--------------|
| 57a607   | imker‑schw(M) | 0 8 * * *    |
```
**Maximale Breite ≤40 Zeichen** (Mobile‑Optimierung). Bei Bedarf Spalten kürzen/abbrechen.

**Weitere bekannte Issues:**
- Telegram bold/italic entities nicht als Markdown im Agent‑Prompt (#52859)
- Nachrichten mit Zeilenumbrüchen werden gesplittet (#47454)

## Installierte Skills (Clawhub)
- **`openclaw‑safe‑change‑flow`** (englisch) – Sichere Config‑Änderungen mit Backup, Validierung, Rollback
- **`config‑safe`** (chinesisch) – Dokumentation für sichere Config‑Änderungen (nicht aktiv genutzt)

---
*Letzte Aktualisierung: 2026-04-18 (Mara‑Roblox‑Interessen) | Clawdia 🦞*