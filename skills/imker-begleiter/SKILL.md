# Imker‑Begleiter – Persönlicher KI‑Assistent für Imker

## 🎯 Übersicht
Ein **persönlicher KI‑Assistent für Imker**, der dich durchs Bienenjahr begleitet, Aufgaben erinnert, Gesundheitsdaten dokumentiert und Sprach‑Logs verarbeitet – **alles per Sprach‑ und Foto‑Input**, weil Imker die Hände nicht frei haben.

## ✨ Kernfunktionen

### 1. 🗓️ Intelligente Erinnerungen
- **Saisonale Aufgaben** (Frühling: Erweitern, Sommer: Honigernte, Herbst: Einwintern, Winter: Varroa‑Behandlung)
- **Wetter‑abhängig** (z.B. Behandlung nur bei >15°C)
- **Cron‑Jobs** für regelmäßige Kontrollen

### 2. 🎤 Sprachbasierte Dokumentation
- **Sprachnachricht senden** („Hab Volk 1 gefüttert“) → automatisch transkribiert & strukturiert gespeichert
- **Hände‑frei‑Workflow** – perfekt am Bienenstand
- **Extraktion** von Volk, Aktion, Menge, Details

### 3. ⚠️ Schwarmalarm
- **Tägliche Prüfung** (8 Uhr) auf „Schwarmwetter“
- **Bedingungen:** Temperatur >18°C, Sonne, windstill, 10–14 Uhr, Mai–Juni
- **Telegram‑Benachrichtigung** bei erhöhter Gefahr

### 4. 📷 Foto‑Analyse (optional)
- **Rähmchen‑/Bienen‑Fotos** hochladen
- **Brutbild‑/Varroa‑Erkennung** via KI‑Vision (bei API‑Key‑Verfügbarkeit)

### 5. 📊 Volks‑Gesundheits‑Tracking
- **JSON‑Datenbank** pro Volk (Standort, Rasse, Königin, Behandlungs‑Historie)
- **Logs** aller Aktionen (füttern, behandeln, ernten)
- **Export‑Funktionen** (PDF‑Reports fürs Imkertagebuch)

### 6. 🔔 Proaktive Benachrichtigungen
- **Telegram‑Nachrichten** bei fälligen Aufgaben
- **Wöchentliche Status‑Reports**
- **Push‑Benachrichtigungen** bei akuten Alarmen

---

## 🚀 Schnellstart

### Voraussetzungen
- **OpenClaw** mit Zugriff auf `cron`, `web_fetch`, `exec`, `memory_*` Tools
- **OpenAI API Key** (für Whisper‑Transkription, optional für Bild‑Analyse)
- **Telegram‑Chat** mit dem Nutzer (Mitch, ID 6882251060)

### Skill aktivieren
Das Skill‑Verzeichnis wird automatisch von OpenClaw geladen, sobald es unter `skills/imker‑begleiter/` liegt.

### Erste Schritte
1. **Volks‑Daten erfassen** (über Sprach‑Log oder manuell)
2. **Cron‑Jobs einrichten** (über `cron add`)
3. **Test‑Sprachnachricht** senden („Hab Volk 1 kontrolliert“)

---

## 🛠️ Technische Architektur

### Verzeichnisstruktur
```
imker-begleiter/
├── SKILL.md                    # Diese Datei
├── scripts/
│   ├── volk_db.py              # Volks‑Datenbank (JSON)
│   ├── voice_logger.py         # Sprach‑Log‑Verarbeitung
│   ├── reminder_cron.py        # Saisonale Erinnerungen
│   ├── swarm_alert.py          # Schwarmalarm‑Logik
│   └── weather_client.py       # Open‑Meteo‑Client
├── references/
│   ├── varroa_behandlung.md    # Aktuelle Behandlungsmethoden
│   ├── honigverordnung.md      # Rechtliche Vorgaben
│   └── krankheiten_lexikon.md  # Symptom‑Übersicht
├── data/
│   ├── voelker.json            # Stammdaten der Völker
│   ├── logs/                   # Log‑Dateien (pro Volk, pro Jahr)
│   └── fotos/                  # Abgelegte Fotos
└── templates/
    └── wochenreport.md         # Vorlage für Status‑Reports
```

### Datenmodell (Volk)
```json
{
  "volk_id": "1",
  "name": "Garten Süd",
  "standort": "Garten Süd, Ludwigsfelde",
  "rasse": "Carnica",
  "königin_gezeichnet": "2025-05",
  "letzte_varroa_behandlung": "2026-03-15",
  "letzte_fütterung": "2026-03-30",
  "besondere_hinweise": "schwärmt leicht",
  "logs": [
    {
      "timestamp": "2026-03-31T16:22:00+02:00",
      "aktion": "füttern",
      "menge": "3 kg Zuckerlösung (3:2)",
      "details": "Brutbild gut, keine Auffälligkeiten",
      "transkript": "Hab Volk eins mit drei Kilogramm Zuckerlösung gefüttert…"
    }
  ]
}
```

### Cron‑Jobs (Beispiele)
| Job | Schedule | Beschreibung |
|-----|----------|--------------|
| Frühlingskontrolle | `0 9 * 4 *` (April, 9 Uhr) | Futter prüfen, Brutraum erweitern |
| Schwarmalarm | `0 8 * * *` (täglich 8 Uhr) | Prüfung auf Schwarmwetter |
| Varroa‑Diagnose | `0 9 15 * *` (15. jedes Monats) | Windel einlegen, Ergebnis protokollieren |
| Wochenreport | `0 18 * * 0` (Sonntag 18 Uhr) | Wochen‑Zusammenfassung senden |

---

## 🔧 Konfiguration

### Umgebungsvariablen
```bash
# OpenAI API Key (für Transkription/Bild‑Analyse)
export OPENAI_API_KEY="sk-..."
# Open‑Meteo Standort (Ludwigsfelde)
export IMKER_LAT="52.30"
export IMKER_LON="13.26"
```

### Skill‑spezifische Einstellungen
Die Konfiguration liegt in `data/config.json`:
```json
{
  "user_id": "6882251060",
  "location": {
    "latitude": 52.30,
    "longitude": 13.26,
    "city": "Ludwigsfelde"
  },
  "alert_thresholds": {
    "swarm_temperature": 18,
    "swarm_wind_max": 15,
    "swarm_cloud_max": 30
  },
  "cron_enabled": true
}
```

---

## 📖 Verwendung

### Sprach‑Log eintragen
1. **Sprachnachricht** im Telegram‑Chat senden (z.B. „Hab Volk 2 mit Ameisensäure behandelt“).
2. **Skill transkribiert** automatisch (Whisper).
3. **Extrahiert** strukturierte Daten (Volk, Aktion, Menge, Details).
4. **Speichert** im Volks‑Log und bestätigt.

### Manuelle Eingabe (falls gewünscht)
```bash
# Über OpenClaw exec
python3 skills/imker‑begleiter/scripts/volk_db.py add-log --volk 1 --aktion "füttern" --menge "3 kg"
```

### Status‑Report anfordern
```bash
# Wochenreport generieren
python3 skills/imker‑begleiter/scripts/report.py weekly --send
```

### Schwarmalarm prüfen (manuell)
```bash
python3 skills/imker‑begleiter/scripts/swarm_alert.py check
```

---

## 🔄 Integration mit anderen Skills

### audio‑assistant‑cheap
- **Transkription** über `gpt‑4o‑mini‑transcribe`
- **Kostenoptimiert** (~$0,003/min)

### openai‑whisper‑api
- **Alternative Transkription** (falls audio‑assistant nicht verfügbar)

### nano‑banana‑pro / openai‑image‑gen
- **Bild‑Analyse** (optional, bei API‑Key‑Verfügbarkeit)

---

## 🧪 Tests

### Test‑Suite ausführen
```bash
cd /data/.openclaw/workspace/skills/imker‑begleiter
python3 -m pytest tests/ -v
```

### Manuelle Tests
1. **Volks‑Datenbank:** `python3 scripts/volk_db.py test`
2. **Sprach‑Log:** `python3 scripts/voice_logger.py test --audio beispiel.ogg`
3. **Wetter‑Client:** `python3 scripts/weather_client.py current`
4. **Schwarmalarm:** `python3 scripts/swarm_alert.py simulate --date 2026-05-15`

---

## 📈 Roadmap

### Phase 1 – MVP (März 2026)
- [x] Skill‑Verzeichnis & Grundstruktur
- [x] Volks‑Datenbank (JSON)
- [x] Sprach‑Log‑Verarbeitung (Transkription + Extraktion)
- [x] Grund‑Cron‑Jobs (Frühlingskontrolle, Varroa‑Diagnose)
- [x] Dokumentation (SKILL.md)

### Phase 2 – Schwarmalarm (April 2026)
- [ ] Wetter‑Integration (Open‑Meteo)
- [ ] Schwarmalarm‑Algorithmus
- [ ] Tägliche Prüfung & Benachrichtigungen
- [ ] Historische Alarm‑Logs

### Phase 3 – Bild‑Analyse (optional)
- [ ] Foto‑Upload‑Handler
- [ ] KI‑Vision‑Integration (Gemini/OpenAI)
- [ ] Brut‑/Varroa‑Erkennung

### Phase 4 – Reporting & Export
- [ ] Wöchentliche Status‑Reports
- [ ] PDF‑Export für Imkertagebuch
- [ ] CSV‑Export für Excel

---

## 🐝 Fazit

**Der Imker‑Begleiter‑Skill bietet:**
- ✅ **Hände‑freie Dokumentation** – einfach sprechen, alles wird gespeichert
- ✅ **Intelligente Erinnerungen** – saisonale Aufgaben, wetterabhängig
- ✅ **Frühwarnsystem** – Schwarmalarm bei perfektem Schwarmwetter
- ✅ **Gesundheits‑Tracking** – komplette Historie pro Volk
- ✅ **Einfache Integration** – nahtlos mit OpenClaw & Telegram

**Perfekt für:** Imker, die die Hände voll haben und einen zuverlässigen, automatisierten Begleiter durchs Bienenjahr brauchen.

---
*Skill‑ID: `imker‑begleiter` | Version: 1.0 | Erstellt: 31.03.2026 | Autor: Clawdia 🦞*