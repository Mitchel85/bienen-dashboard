#!/usr/bin/env python3
"""
Volks‑Datenbank für den Imker‑Begleiter‑Skill.
Verwaltet Stammdaten der Völker und Log‑Einträge (JSON‑basiert).
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# Pfade
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
VOELKER_JSON = DATA_DIR / "voelker.json"
LOGS_DIR = DATA_DIR / "logs"
CONFIG_JSON = DATA_DIR / "config.json"

# Sicherstellen, dass Verzeichnisse existieren
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

def load_voelker() -> Dict[str, Any]:
    """Lädt die Volks‑Datenbank aus voelker.json."""
    if not VOELKER_JSON.exists():
        return {}
    try:
        with open(VOELKER_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_voelker(data: Dict[str, Any]) -> None:
    """Speichert die Volks‑Datenbank in voelker.json."""
    with open(VOELKER_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_config() -> Dict[str, Any]:
    """Lädt die Skill‑Konfiguration."""
    if not CONFIG_JSON.exists():
        return {}
    try:
        with open(CONFIG_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def init_sample_voelker() -> None:
    """Legt zwei Beispiel‑Völker an (falls Datenbank leer)."""
    voelker = load_voelker()
    if voelker:
        return
    
    sample = {
        "1": {
            "volk_id": "1",
            "name": "Garten Süd",
            "standort": "Garten Süd, Ludwigsfelde",
            "rasse": "Carnica",
            "königin_gezeichnet": "2025-05",
            "letzte_varroa_behandlung": "2026-03-15",
            "letzte_fütterung": "2026-03-30",
            "besondere_hinweise": "schwärmt leicht",
            "logs": []
        },
        "2": {
            "volk_id": "2",
            "name": "Terrasse",
            "standort": "Terrasse, Ludwigsfelde",
            "rasse": "Buckfast",
            "königin_gezeichnet": "2025-07",
            "letzte_varroa_behandlung": "2026-03-10",
            "letzte_fütterung": "2026-03-28",
            "besondere_hinweise": "sanftmütig",
            "logs": []
        }
    }
    save_voelker(sample)
    print("✅ Zwei Beispiel‑Völker angelegt (IDs: 1, 2).")

def add_log(volk_id: str, aktion: str, menge: str = "", details: str = "", transkript: str = "") -> Dict[str, Any]:
    """
    Fügt einen Log‑Eintrag zum angegebenen Volk hinzu.
    
    Args:
        volk_id: ID des Volkes (z.B. "1")
        aktion: Art der Aktion (z.B. "füttern", "behandeln", "kontrollieren")
        menge: Menge (z.B. "3 kg Zuckerlösung")
        details: Freitext‑Details
        transkript: Original‑Transkript (falls aus Sprach‑Log)
    
    Returns:
        Der erstellte Log‑Eintrag.
    """
    voelker = load_voelker()
    if volk_id not in voelker:
        raise ValueError(f"Volk {volk_id} existiert nicht.")
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "aktion": aktion,
        "menge": menge,
        "details": details
        # transkript wird nur gespeichert, wenn nicht leer (User-Wunsch)
    }
    if transkript:
        log_entry["transkript"] = transkript
    
    voelker[volk_id].setdefault("logs", []).append(log_entry)
    
    # Je nach Aktion bestimmte Felder aktualisieren
    if aktion == "füttern":
        voelker[volk_id]["letzte_fütterung"] = datetime.now().strftime("%Y-%m-%d")
    elif aktion == "varroa_behandlung":
        voelker[volk_id]["letzte_varroa_behandlung"] = datetime.now().strftime("%Y-%m-%d")
    
    save_voelker(voelker)
    
    # Separaten Log‑Datei‑Eintrag (für Backup)
    log_file = LOGS_DIR / f"{volk_id}_{datetime.now().strftime('%Y-%m')}.json"
    logs = []
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
    logs.append(log_entry)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    return log_entry

def get_volk(volk_id: str) -> Optional[Dict[str, Any]]:
    """Gibt das Volk mit der angegebenen ID zurück."""
    voelker = load_voelker()
    return voelker.get(volk_id)

def list_voelker() -> List[Dict[str, Any]]:
    """Gibt eine Liste aller Völker zurück."""
    voelker = load_voelker()
    return [v for k, v in voelker.items() if k != "meta"]

def get_recent_logs(volk_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Gibt die neuesten Log‑Einträge zurück (optional für ein bestimmtes Volk).
    
    Args:
        volk_id: Optionale Filterung auf ein Volk
        limit: Maximale Anzahl zurückzugebender Einträge
    
    Returns:
        Liste der Log‑Einträge (neueste zuerst).
    """
    voelker = load_voelker()
    all_logs = []
    
    for vid, volk in voelker.items():
        if volk_id and vid != volk_id:
            continue
        for log in volk.get("logs", []):
            log_copy = log.copy()
            log_copy["volk_id"] = vid
            all_logs.append(log_copy)
    
    # Nach Timestamp sortieren (neueste zuerst)
    all_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return all_logs[:limit]

def update_volk(volk_id: str, **updates) -> Dict[str, Any]:
    """
    Aktualisiert Felder eines Volkes.
    
    Args:
        volk_id: ID des Volkes
        **updates: Schlüssel‑Wert‑Paare der zu aktualisierenden Felder
    
    Returns:
        Das aktualisierte Volk.
    """
    voelker = load_voelker()
    if volk_id not in voelker:
        raise ValueError(f"Volk {volk_id} existiert nicht.")
    
    voelker[volk_id].update(updates)
    save_voelker(voelker)
    return voelker[volk_id]

def delete_volk(volk_id: str) -> bool:
    """Löscht ein Volk (und seine Logs)."""
    voelker = load_voelker()
    if volk_id not in voelker:
        return False
    
    del voelker[volk_id]
    save_voelker(voelker)
    
    # Log‑Dateien löschen (optional, hier behalten wir sie als Archiv)
    # for log_file in LOGS_DIR.glob(f"{volk_id}_*.json"):
    #     log_file.unlink()
    
    return True

# CLI für manuelle Tests
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Volks‑Datenbank für Imker‑Begleiter")
    subparsers = parser.add_subparsers(dest="command", help="Befehl")
    
    # init
    subparsers.add_parser("init", help="Legt Beispiel‑Völker an")
    
    # list
    subparsers.add_parser("list", help="Listet alle Völker auf")
    
    # show
    show_parser = subparsers.add_parser("show", help="Zeigt ein bestimmtes Volk")
    show_parser.add_argument("volk_id", help="ID des Volkes")
    
    # add-log
    log_parser = subparsers.add_parser("add-log", help="Fügt einen Log‑Eintrag hinzu")
    log_parser.add_argument("volk_id", help="ID des Volkes")
    log_parser.add_argument("aktion", help="Art der Aktion (z.B. 'füttern')")
    log_parser.add_argument("--menge", default="", help="Menge (z.B. '3 kg')")
    log_parser.add_argument("--details", default="", help="Freitext‑Details")
    log_parser.add_argument("--transkript", default="", help="Original‑Transkript")
    
    # recent-logs
    recent_parser = subparsers.add_parser("recent-logs", help="Zeigt neueste Log‑Einträge")
    recent_parser.add_argument("--volk", help="Filter nach Volk‑ID")
    recent_parser.add_argument("--limit", type=int, default=10, help="Anzahl Einträge")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_sample_voelker()
        print("✅ Volks‑Datenbank initialisiert.")
        
    elif args.command == "list":
        voelker = list_voelker()
        for volk in voelker:
            print(f"{volk['volk_id']}: {volk['name']} ({volk['standort']})")
            print(f"  Rasse: {volk['rasse']}, Königin: {volk['königin_gezeichnet']}")
            print(f"  Letzte Fütterung: {volk.get('letzte_fütterung', '—')}")
            print(f"  Letzte Varroa‑Behandlung: {volk.get('letzte_varroa_behandlung', '—')}")
            print()
    
    elif args.command == "show":
        volk = get_volk(args.volk_id)
        if volk:
            print(json.dumps(volk, ensure_ascii=False, indent=2))
        else:
            print(f"Volk {args.volk_id} nicht gefunden.")
    
    elif args.command == "add-log":
        log = add_log(args.volk_id, args.aktion, args.menge, args.details, args.transkript)
        print(f"✅ Log‑Eintrag hinzugefügt:")
        print(json.dumps(log, ensure_ascii=False, indent=2))
    
    elif args.command == "recent-logs":
        logs = get_recent_logs(args.volk, args.limit)
        for log in logs:
            ts = log.get("timestamp", "???")
            volk = log.get("volk_id", "?")
            aktion = log.get("aktion", "—")
            menge = log.get("menge", "")
            print(f"{ts} | Volk {volk} | {aktion} {menge}")
    
    else:
        parser.print_help()