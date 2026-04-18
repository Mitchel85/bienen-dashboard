#!/usr/bin/env python3
"""
Sprach‑Log‑Verarbeitung für den Imker‑Begleiter‑Skill.
Transkribiert Audio‑Dateien und extrahiert strukturierte Log‑Einträge.
"""
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

# Pfade
SKILL_DIR = Path(__file__).parent.parent
WHISPER_SCRIPT = Path("/usr/lib/node_modules/openclaw/skills/openai-whisper-api/scripts/transcribe.sh")

def transcribe_audio(audio_path: Path, language: str = "de") -> str:
    """
    Transkribiert eine Audio‑Datei mit OpenAI Whisper (über vorhandenen Skill).
    
    Args:
        audio_path: Pfad zur Audio‑Datei (.ogg, .mp3, .wav, .m4a)
        language: Sprache (ISO‑639‑1, z.B. "de")
    
    Returns:
        Transkript als String.
    
    Raises:
        FileNotFoundError: Wenn Audio‑Datei oder Whisper‑Script nicht existiert.
        RuntimeError: Wenn Transkription fehlschlägt.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio‑Datei nicht gefunden: {audio_path}")
    
    if not WHISPER_SCRIPT.exists():
        # Fallback: audio-assistant-cheap oder direkte OpenAI‑API
        raise FileNotFoundError(f"Whisper‑Script nicht gefunden: {WHISPER_SCRIPT}")
    
    # Whisper‑Script aufrufen
    cmd = [str(WHISPER_SCRIPT), str(audio_path), "--language", language]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output_file = result.stdout.strip()
        if not output_file:
            raise RuntimeError("Whisper‑Script gab keine Ausgabedatei zurück.")
        
        with open(output_file, "r", encoding="utf-8") as f:
            transcript = f.read().strip()
        
        # Temporäre Text‑Datei löschen (optional)
        # Path(output_file).unlink()
        
        return transcript
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Transkription fehlgeschlagen: {e.stderr}") from e

def parse_transcript(transcript: str) -> Dict[str, str]:
    """
    Extrahiert strukturierte Daten aus einem Transkript.
    
    Erwartete Muster:
    - "Hab Volk 1 mit 3 kg Zuckerlösung gefüttert"
    - "Volk 2 kontrolliert, Brutbild gut"
    - "Varroa‑Behandlung bei Volk 1 mit Ameisensäure"
    - "Hab bei Volk 2 die Windel eingelegt"
    
    Returns:
        Dictionary mit keys: volk_id, aktion, menge, details
    """
    # Normalisieren: Kleinschreibung, Satzzeichen entfernen
    text = transcript.lower().strip(" .")
    
    # Default‑Werte
    result = {
        "volk_id": None,
        "aktion": None,
        "menge": "",
        "details": "",
        "original": transcript
    }
    
    # Volk‑ID extrahieren (Muster: "volk 1", "volk1", "volk eins")
    volk_match = re.search(r'volk\s*(\d+|eins|zwei|drei|vier)', text)
    if volk_match:
        num = volk_match.group(1)
        if num.isdigit():
            result["volk_id"] = num
        else:
            mapping = {"eins": "1", "zwei": "2", "drei": "3", "vier": "4"}
            result["volk_id"] = mapping.get(num, "1")
    
    # Aktion erkennen (Schlüsselwörter)
    action_keywords = {
        "füttern": "füttern",
        "gefüttert": "füttern",
        "fütterung": "füttern",
        "behandeln": "varroa_behandlung",
        "behandlung": "varroa_behandlung",
        "ameisensäure": "varroa_behandlung",
        "oxalsäure": "varroa_behandlung",
        "thymol": "varroa_behandlung",
        "kontrollieren": "kontrollieren",
        "kontrolliert": "kontrollieren",
        "kontrolle": "kontrollieren",
        "windel": "varroa_diagnose",
        "windel eingelegt": "varroa_diagnose",
        "erweitert": "erweitern",
        "erweitern": "erweitern",
        "honig": "honigernte",
        "geschleudert": "honigernte",
        "schwarm": "schwarmkontrolle",
        "schwarmzelle": "schwarmkontrolle"
    }
    
    for keyword, aktion in action_keywords.items():
        if keyword in text:
            result["aktion"] = aktion
            break
    
    # Menge extrahieren (Zahl + Einheit)
    menge_match = re.search(r'(\d+[\.,]?\d*)\s*(kg|g|ml|l|prozent|%)', text)
    if menge_match:
        result["menge"] = f"{menge_match.group(1)} {menge_match.group(2)}"
    
    # Details: Rest des Transkripts, ohne Volk/Aktion/Menge
    details = text
    if volk_match:
        details = details.replace(volk_match.group(0), "")
    # Entferne bekannte Aktionen
    if result["aktion"]:
        for kw in action_keywords:
            details = details.replace(kw, "")
    
    # Aufräumen: Mehrfache Leerzeichen, führende/folgende Satzzeichen
    details = re.sub(r'\s+', ' ', details).strip(" ,.;")
    if details:
        result["details"] = details
    
    return result

def process_audio_log(audio_path: Path, language: str = "de") -> Dict[str, str]:
    """
    Kompletter Workflow: Audio transkribieren, parsen, Log‑Eintrag erstellen.
    
    Args:
        audio_path: Pfad zur Audio‑Datei
        language: Sprache für Transkription
    
    Returns:
        Dictionary mit transkript und geparsten Daten.
    """
    transcript = transcribe_audio(audio_path, language)
    parsed = parse_transcript(transcript)
    
    # Transkript wird NICHT gespeichert (User-Wunsch)
    # parsed["transkript"] = transcript
    
    return parsed

def save_log_to_db(parsed_data: Dict[str, str]) -> Dict[str, any]:
    """
    Speichert einen geparsten Log‑Eintrag in der Volks‑Datenbank.
    
    Args:
        parsed_data: Dictionary mit volk_id, aktion, menge, details, transkript
    
    Returns:
        Der gespeicherte Log‑Eintrag (wie von volk_db.add_log zurückgegeben).
    """
    # Import hier, um Zirkuläre Abhängigkeiten zu vermeiden
    volk_db_path = SKILL_DIR / "scripts" / "volk_db.py"
    if not volk_db_path.exists():
        raise ImportError("Volks‑Datenbank‑Skript nicht gefunden.")
    
    # Füge den Pfad zum Python‑Pfad hinzu
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        from volk_db import add_log
    except ImportError as e:
        raise ImportError(f"Konnte volk_db nicht importieren: {e}")
    
    volk_id = parsed_data.get("volk_id")
    if not volk_id:
        raise ValueError("Keine volk_id in geparsten Daten gefunden.")
    
    log_entry = add_log(
        volk_id=volk_id,
        aktion=parsed_data.get("aktion", "unbekannt"),
        menge=parsed_data.get("menge", ""),
        details=parsed_data.get("details", "")
        # transkript wird nicht gespeichert (User-Wunsch)
    )
    
    return log_entry

# CLI für manuelle Tests
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sprach‑Log‑Verarbeitung für Imker‑Begleiter")
    subparsers = parser.add_subparsers(dest="command", help="Befehl")
    
    # transcribe
    trans_parser = subparsers.add_parser("transcribe", help="Transkribiert eine Audio‑Datei")
    trans_parser.add_argument("audio_file", help="Pfad zur Audio‑Datei")
    trans_parser.add_argument("--language", default="de", help="Sprache (z.B. de, en)")
    
    # parse
    parse_parser = subparsers.add_parser("parse", help="Parst ein Transkript (aus Datei oder stdin)")
    parse_parser.add_argument("--file", help="Datei mit Transkript")
    parse_parser.add_argument("--text", help="Transkript als Text")
    
    # process
    process_parser = subparsers.add_parser("process", help="Kompletter Workflow: Audio → Transkript → Parse → DB")
    process_parser.add_argument("audio_file", help="Pfad zur Audio‑Datei")
    process_parser.add_argument("--language", default="de", help="Sprache")
    process_parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, nicht in DB speichern")
    
    args = parser.parse_args()
    
    if args.command == "transcribe":
        try:
            transcript = transcribe_audio(Path(args.audio_file), args.language)
            print("📝 Transkript:")
            print(transcript)
        except Exception as e:
            print(f"❌ Fehler: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "parse":
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        elif args.text:
            text = args.text
        else:
            # Von stdin lesen
            text = sys.stdin.read()
        
        parsed = parse_transcript(text)
        print("🎯 Geparste Daten:")
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    
    elif args.command == "process":
        try:
            parsed = process_audio_log(Path(args.audio_file), args.language)
            print("✅ Verarbeitet:")
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
            
            if not args.dry_run:
                log_entry = save_log_to_db(parsed)
                print("💾 In Datenbank gespeichert:")
                print(json.dumps(log_entry, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"❌ Fehler: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()