#!/usr/bin/env python3
"""
Saisonale Erinnerungen für den Imker‑Begleiter‑Skill.
Generiert monatliche Aufgaben‑Listen und sendet Benachrichtigungen.
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Pfade
SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "data" / "config.json"
VOELKER_FILE = SKILL_DIR / "data" / "voelker.json"

def load_config() -> Dict[str, Any]:
    """Lädt die Skill‑Konfiguration."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def load_voelker() -> Dict[str, Any]:
    """Lädt die Volks‑Datenbank."""
    if not VOELKER_FILE.exists():
        return {}
    try:
        with open(VOELKER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def get_monthly_tasks(month: int) -> List[str]:
    """
    Gibt eine Liste saisonaler Aufgaben für den gegebenen Monat zurück.
    
    Quelle: Imker‑Kalender (Mitteleuropa)
    """
    tasks = {
        1: [
            "⚠️ Varroa‑Diagnose: Windel einlegen, Milben zählen",
            "📦 Futter prüfen, ggf. nachfüttern (Zuckerteig)",
            "❄️ Flugloch auf Schneefreiheit kontrollieren"
        ],
        2: [
            "🔍 Volkskontrolle (kurz, bei >10°C): Brut? Futter?",
            "📊 Varroa‑Diagnose auswerten, ggf. Oxalsäure‑Nachbehandlung",
            "🛠️ Material für Frühjahr vorbereiten (Rähmchen, Mittelwände)"
        ],
        3: [
            "🌱 Erste große Durchsicht bei >15°C",
            "🍯 Futter prüfen, ggf. Auflösung von Futterwaben",
            "👑 Königin suchen, ggf. Neubewertung"
        ],
        4: [
            "🌼 Brutraum erweitern (zweite Zarge bei Bedarf)",
            "🐝 Schwarmkontrolle beginnen (Mai/Juni‑Vorbereitung)",
            "💉 Erste Varroa‑Behandlung planen (Ameisensäure)"
        ],
        5: [
            "🚨 Intensiv‑Schwarmkontrolle (wöchentlich)",
            "🍯 Honigraum aufsetzen (bei Trachtbeginn)",
            "👑 Ablegerbildung (falls Schwarmstimmung)"
        ],
        6: [
            "🍯 Honigernte vorbereiten (Schleuder, Gläser)",
            "🚨 Schwarmkontrolle fortsetzen",
            "💉 Varroa‑Behandlung nach Honigernte"
        ],
        7: [
            "🍯 Honigernte durchführen (bei Trachtende)",
            "🐝 Völker auf Weiselrichtigkeit prüfen",
            "💉 Ameisensäure‑Behandlung starten"
        ],
        8: [
            "💉 Varroa‑Behandlung fortsetzen",
            "🍂 Futtermenge berechnen (Einwintern)",
            "👑 Königin‑Bewertung (Leistung, Sanftmut)"
        ],
        9: [
            "🍯 Einfüttern abschließen (Zuckerlösung 3:2)",
            "🐝 Völker auf Stärke reduzieren (Wintergröße)",
            "💉 Oxalsäure‑Behandlung vorbereiten"
        ],
        10: [
            "❄️ Winterfest machen: Beuten isolieren, Mäuseschutz",
            "💉 Oxalsäure‑Behandlung (bei brutfreiem Zustand)",
            "📊 Jahresbilanz: Honigertrag, Volksentwicklung"
        ],
        11: [
            "🔍 Kurzkontrolle: Futter, Flugloch, Beuten‑Sicherheit",
            "📦 Material einlagern, Werkzeug reinigen",
            "📝 Imkertagebuch für das Jahr abschließen"
        ],
        12: [
            "🎄 Ruhephase – nur Störungen vermeiden",
            "📅 Planung für nächstes Jahr: Ziele, Anschaffungen",
            "🛠️ Wartung: Schleuder, Smoker, Schutzausrüstung"
        ]
    }
    return tasks.get(month, ["✅ Dieser Monat hat keine spezifischen Aufgaben."])

def get_overdue_tasks() -> List[str]:
    """
    Ermittelt überfällige Aufgaben basierend auf Volks‑Daten.
    
    Prüft:
    - Letzte Varroa‑Behandlung > 3 Monate?
    - Letzte Fütterung > 30 Tage (im Herbst)?
    - Fehlende Königin‑Markierung?
    """
    voelker = load_voelker()
    now = datetime.now()
    overdue = []
    
    for volk_id, volk in voelker.items():
        name = volk.get("name", f"Volk {volk_id}")
        
        # Varroa‑Behandlung
        last_varroa = volk.get("letzte_varroa_behandlung")
        if last_varroa:
            try:
                last_date = datetime.strptime(last_varroa, "%Y-%m-%d")
                if (now - last_date).days > 90:  # 3 Monate
                    overdue.append(f"⚠️ {name}: Varroa‑Behandlung überfällig (>90 Tage)")
            except ValueError:
                pass
        
        # Fütterung (nur September–Oktober relevant)
        if now.month in (9, 10):
            last_feed = volk.get("letzte_fütterung")
            if last_feed:
                try:
                    last_date = datetime.strptime(last_feed, "%Y-%m-%d")
                    if (now - last_date).days > 30:
                        overdue.append(f"⚠️ {name}: Einfütterung überfällig (>30 Tage)")
                except ValueError:
                    pass
        
        # Königin‑Markierung älter als 2 Jahre?
        queen_mark = volk.get("königin_gezeichnet")
        if queen_mark and len(queen_mark) == 7:  # Format "2025‑05"
            try:
                mark_year = int(queen_mark[:4])
                if now.year - mark_year >= 2:
                    overdue.append(f"👑 {name}: Königin möglicherweise zu alt (gezeichnet {queen_mark})")
            except ValueError:
                pass
    
    return overdue

def generate_reminder_message() -> str:
    """
    Generiert eine komplette Erinnerungs‑Nachricht.
    """
    now = datetime.now()
    month = now.month
    month_name = now.strftime("%B")
    
    lines = [
        f"🗓️ Imker‑Erinnerungen – {now.strftime('%d.%m.%Y')}",
        f"",
        f"📅 **Saisonale Aufgaben für {month_name}:**"
    ]
    
    tasks = get_monthly_tasks(month)
    for task in tasks:
        lines.append(f"• {task}")
    
    lines.append("")
    lines.append("⏰ **Überfällige Aufgaben:**")
    overdue = get_overdue_tasks()
    if overdue:
        for task in overdue:
            lines.append(f"• {task}")
    else:
        lines.append("• Keine überfälligen Aufgaben – gut gemacht!")
    
    lines.append("")
    lines.append("🐝 **Aktuelle Völker‑Übersicht:**")
    voelker = load_voelker()
    if voelker:
        for volk_id, volk in voelker.items():
            name = volk.get("name", f"Volk {volk_id}")
            last_feed = volk.get("letzte_fütterung", "—")
            last_varroa = volk.get("letzte_varroa_behandlung", "—")
            lines.append(f"• {name}: Fütterung {last_feed}, Varroa {last_varroa}")
    else:
        lines.append("• Noch keine Völker angelegt.")
    
    lines.append("")
    lines.append("📌 *Tipp: Sprach‑Logs einfach per Sprachnachricht senden!*")
    
    return "\n".join(lines)

def send_reminder(user_id: str = None, dry_run: bool = False) -> bool:
    """
    Sendet die Erinnerungs‑Nachricht an den Benutzer.
    
    Args:
        user_id: Telegram‑ID (falls nicht in config)
        dry_run: Nur generieren, nicht senden
    
    Returns:
        True bei Erfolg, False sonst.
    """
    config = load_config()
    if not user_id:
        user_id = config.get("user_id")
    if not user_id:
        print("❌ Keine user_id in Konfiguration gefunden.", file=sys.stderr)
        return False
    
    message = generate_reminder_message()
    
    if dry_run:
        print("📨 DRY‑RUN – Erinnerungs‑Nachricht:")
        print(message)
        return True
    
    # OpenClaw CLI Befehl
    cmd = [
        "openclaw", "message", "send",
        "--channel", "telegram",
        "--target", user_id,
        "--message", message
    ]
    
    try:
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Erinnerungs‑Nachricht gesendet.")
            return True
        else:
            print(f"❌ OpenClaw send fehlgeschlagen: {result.stderr}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"❌ Ausführen von openclaw message send fehlgeschlagen: {e}", file=sys.stderr)
        return False

def main() -> None:
    """
    Hauptfunktion für CLI und Cron‑Job.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Saisonale Erinnerungen für Imker‑Begleiter")
    parser.add_argument("--dry-run", action="store_true", help="Nur generieren, nicht senden")
    parser.add_argument("--month", type=int, help="Monat (1‑12, default aktuell)")
    parser.add_argument("--send", action="store_true", help="Nachricht senden (sonst nur anzeigen)")
    args = parser.parse_args()
    
    if args.month:
        tasks = get_monthly_tasks(args.month)
        print(f"📅 Aufgaben für Monat {args.month}:")
        for task in tasks:
            print(f"• {task}")
        overdue = get_overdue_tasks()
        if overdue:
            print("\n⏰ Überfällig:")
            for task in overdue:
                print(f"• {task}")
    else:
        message = generate_reminder_message()
        if args.dry_run or not args.send:
            print(message)
        
        if args.send:
            success = send_reminder(dry_run=args.dry_run)
            sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()