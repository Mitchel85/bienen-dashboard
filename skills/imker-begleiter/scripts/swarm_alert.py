#!/usr/bin/env python3
"""
Schwarmalarm für den Imker‑Begleiter‑Skill.
Prüft täglich auf Schwarmwetter und sendet bei Gefahr eine Telegram‑Benachrichtigung.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple

# Pfade
SKILL_DIR = Path(__file__).parent.parent
CONFIG_FILE = SKILL_DIR / "data" / "config.json"

# Importiere Wetter‑Client
sys.path.insert(0, str(SKILL_DIR / "scripts"))
try:
    from weather_client import get_current_weather, is_swarm_weather
except ImportError as e:
    print(f"❌ Wetter‑Client kann nicht importiert werden: {e}", file=sys.stderr)
    sys.exit(1)

def load_config() -> Dict[str, Any]:
    """Lädt die Skill‑Konfiguration."""
    if not CONFIG_FILE.exists():
        print(f"⚠️ Konfigurationsdatei nicht gefunden: {CONFIG_FILE}", file=sys.stderr)
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ Konfigurationsdatei kann nicht gelesen werden: {e}", file=sys.stderr)
        return {}

def send_telegram_alert(message: str, user_id: str = None) -> bool:
    """
    Sendet eine Nachricht an den Benutzer via OpenClaw message send.
    
    Args:
        message: Text der Benachrichtigung
        user_id: Telegram‑ID (falls nicht in config)
    
    Returns:
        True bei Erfolg, False sonst.
    """
    config = load_config()
    if not user_id:
        user_id = config.get("user_id")
    if not user_id:
        print("❌ Keine user_id in Konfiguration gefunden.", file=sys.stderr)
        return False
    
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
            print(f"✅ Benachrichtigung an {user_id} gesendet.")
            return True
        else:
            print(f"❌ OpenClaw send fehlgeschlagen: {result.stderr}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"❌ Ausführen von openclaw message send fehlgeschlagen: {e}", file=sys.stderr)
        return False

def check_swarm_alert() -> Tuple[bool, str]:
    """
    Prüft aktuelle Wetterbedingungen auf Schwarmgefahr.
    
    Returns:
        Tuple (is_alert: bool, message: str)
    """
    try:
        current = get_current_weather()
    except Exception as e:
        return False, f"❌ Wetterabfrage fehlgeschlagen: {e}"
    
    now = datetime.now()
    hour = now.hour
    month = now.month
    
    # Nur Mai–Juni prüfen (Hauptschwarmzeit)
    if month not in (5, 6):
        return False, f"✅ Keine Schwarmzeit (aktuell {month}. Monat, Schwarmzeit Mai–Juni)."
    
    is_swarm, msg = is_swarm_weather(current, hour_of_day=hour)
    
    if is_swarm:
        alert_msg = f"🚨 SCHWARMALARM – {msg}"
        return True, alert_msg
    else:
        return False, msg

def main() -> None:
    """
    Hauptfunktion für CLI und Cron‑Job.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Schwarmalarm für Imker‑Begleiter")
    parser.add_argument("--dry-run", action="store_true", help="Nur prüfen, keine Benachrichtigung senden")
    parser.add_argument("--verbose", "-v", action="store_true", help="Ausführliche Ausgabe")
    args = parser.parse_args()
    
    is_alert, message = check_swarm_alert()
    
    if args.verbose or args.dry_run:
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(message)
    
    if is_alert and not args.dry_run:
        config = load_config()
        user_id = config.get("user_id")
        if not user_id:
            print("❌ Keine user_id in Konfiguration, Benachrichtigung wird nicht gesendet.", file=sys.stderr)
            sys.exit(1)
        
        success = send_telegram_alert(message, user_id)
        if not success:
            sys.exit(1)
    elif is_alert and args.dry_run:
        print("🚨 DRY‑RUN: Benachrichtigung würde gesendet werden.")
    
    # Exit‑Code: 0 = kein Alarm, 1 = Alarm (für Cron‑Logging)
    sys.exit(0 if not is_alert else 1)

if __name__ == "__main__":
    main()