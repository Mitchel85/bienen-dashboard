#!/usr/bin/env python3
"""
Generiert das Dashboard mit benutzerfreundlichen Termin‑Beschreibungen.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

SKILL_DIR = "/data/.openclaw/workspace/skills/imker-begleiter"
VOELKER_JSON = os.path.join(SKILL_DIR, "data", "voelker.json")
OUTPUT_HTML = "/data/.openclaw/canvas/index.html"
WORKSPACE_HTML = "/data/.openclaw/workspace/index.html"
CRON_CACHE = "/tmp/cronjobs.json"

def load_voelker():
    if not os.path.exists(VOELKER_JSON):
        return {}
    with open(VOELKER_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def get_cronjobs():
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            jobs = data.get("jobs", [])
            with open(CRON_CACHE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"✅ Cronjobs live geladen ({len(jobs)} total)")
        else:
            raise Exception(f"Befehl fehlgeschlagen: {result.stderr[:200]}")
    except Exception as e:
        print(f"⚠️ Live‑Abruf fehlgeschlagen: {e}")
        if os.path.exists(CRON_CACHE):
            with open(CRON_CACHE, "r", encoding="utf-8") as f:
                data = json.load(f)
            jobs = data.get("jobs", [])
            print(f"⚠️ Cronjobs aus Cache geladen ({len(jobs)} total)")
        else:
            jobs = []
            print("⚠️ Keine Cronjobs verfügbar")
    
    relevant = []
    for job in jobs:
        if not job.get("enabled", True):
            continue
        name = job.get("name", "")
        delivery = job.get("delivery", {})
        to = delivery.get("to", "")
        if to == "6882251060" or name.startswith("imker-") or "varroa" in name:
            relevant.append(job)
    return relevant

def format_cron_schedule(job):
    sched = job.get("schedule", {})
    kind = sched.get("kind")
    if kind == "cron":
        expr = sched.get("expr", "")
        tz = sched.get("tz", "")
        tz_str = f" ({tz})" if tz else ""
        return f"Cron: {expr}{tz_str}"
    elif kind == "at":
        at = sched.get("at", "")
        try:
            dt_utc = datetime.fromisoformat(at.replace('Z', '+00:00'))
            return f"Einmalig: {dt_utc.strftime('%d.%m.%Y %H:%M')} UTC"
        except:
            return f"Einmalig: {at}"
    elif kind == "every":
        every_ms = sched.get("everyMs", 0)
        if every_ms >= 86400000:
            days = every_ms // 86400000
            return f"Alle {days} Tag(e)"
        elif every_ms >= 3600000:
            hours = every_ms // 3600000
            return f"Alle {hours} Stunde(n)"
        else:
            minutes = every_ms // 60000
            return f"Alle {minutes} Minute(n)"
    return "Unbekannt"

def format_next_run(job):
    state = job.get("state", {})
    next_ms = state.get("nextRunAtMs")
    if not next_ms:
        return "–"
    try:
        dt = datetime.fromtimestamp(next_ms / 1000, timezone.utc)
        now = datetime.now(timezone.utc)
        diff = dt - now
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        if days > 0:
            return f"{dt.strftime('%d.%m.%Y %H:%M')} UTC (in {days}d {hours}h)"
        elif hours > 0:
            return f"{dt.strftime('%d.%m.%Y %H:%M')} UTC (in {hours}h {minutes}m)"
        else:
            return f"{dt.strftime('%d.%m.%Y %H:%M')} UTC (in {minutes}m)"
    except:
        return "–"

def format_task_description(job):
    """
    Wandelt einen Cron‑Job in eine niederschwellige, lesbare Aufgabenbeschreibung um.
    """
    name = job.get("name", "")
    payload = job.get("payload", {})
    message = payload.get("message", "")
    
    # Mapping von bekannten Namen zu lesbaren Beschreibungen
    name_map = {
        "tägliche-sicherheits-news-maja": "Sicherheitsnews für Maja",
        "imker-schwarmalarm": "Schwarmalarm checken",
        "imker-fruehling": "Frühlingserinnerung",
        "imker-varroa": "Varroa‑Behandlungserinnerung",
        "imker-wochenreport": "Wochenreport erstellen",
        "varroa-auszaehlung-erinnerung": "Varroa‑Windel auszählen"
    }
    
    if name in name_map:
        return name_map[name]
    
    # Falls Name unbekannt, versuche aus der message einen Dateinamen zu extrahieren
    if "Führe" in message and ".py" in message:
        # Extrahiere den Dateinamen (z.B. "swarm_alert.py")
        import re
        match = re.search(r'/([a-zA-Z0-9_]+\.py)', message)
        if match:
            script = match.group(1)
            if script == "swarm_alert.py":
                return "Schwarmalarm checken"
            elif script == "reminder_cron.py":
                return "Erinnerung senden"
    
    # Fallback: Name mit Leerzeichen und Großbuchstaben formatieren
    readable = name.replace("-", " ").replace("_", " ").title()
    return readable

def extract_latest_weight(logs):
    weight = None
    weight_date = None
    for log in reversed(logs):
        if log.get("aktion") == "wiegen" and log.get("menge"):
            try:
                parts = log["menge"].split()
                if parts:
                    weight = float(parts[0])
                    weight_date = log["timestamp"][:10]
                    break
            except:
                pass
    return weight, weight_date

def extract_latest_logs(logs, limit=3):
    return list(reversed(logs))[:limit]

def generate_html(voelker, cronjobs):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    active_volks = sum(1 for v in voelker.values() if v.get("logs"))
    total_logs = sum(len(v.get("logs", [])) for v in voelker.values())
    
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienenvölker Dashboard</title>
    <style>
        * {{ box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        body {{ background-color: #f5f5f5; margin: 0; padding: 20px; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); padding: 30px; }}
        header {{ text-align: center; margin-bottom: 40px; border-bottom: 2px solid #ffcc00; padding-bottom: 20px; }}
        h1 {{ color: #d97706; margin: 0; font-size: 2.5rem; }}
        .subtitle {{ color: #666; font-size: 1.1rem; margin-top: 8px; }}
        .stats {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 40px; }}
        .stat-card {{ flex: 1; min-width: 200px; background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
        .stat-card h3 {{ margin-top: 0; color: #92400e; }}
        .stat-value {{ font-size: 2rem; font-weight: bold; color: #d97706; }}
        .table-container {{ overflow-x: auto; margin-bottom: 40px; border-radius: 10px; border: 1px solid #e5e7eb; }}
        table {{ width: 100%; border-collapse: collapse; min-width: 800px; }}
        th {{ background-color: #f3f4f6; text-align: left; padding: 16px; font-weight: 600; color: #374151; border-bottom: 2px solid #d1d5db; }}
        td {{ padding: 16px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }}
        tr:hover {{ background-color: #f9fafb; }}
        .volk-name {{ font-weight: bold; color: #1f2937; }}
        .volk-id {{ display: inline-block; background: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 20px; font-size: 0.9rem; font-weight: bold; }}
        .log-container, .termine-container {{ margin-top: 50px; }}
        .log-section, .termine-section {{ background: #f8fafc; border-radius: 10px; padding: 20px; margin-bottom: 30px; border-left: 5px solid #10b981; }}
        .termine-section {{ border-left-color: #8b5cf6; }}
        .log-section h3, .termine-section h3 {{ margin-top: 0; color: #047857; }}
        .termine-section h3 {{ color: #7c3aed; }}
        .log-entry, .termin {{ background: white; border-radius: 8px; padding: 16px; margin-bottom: 12px; border-left: 4px solid #3b82f6; box-shadow: 0 2px 4px rgba(0,0,0,0.04); }}
        .termin {{ border-left-color: #8b5cf6; }}
        .log-time, .termin-time {{ font-size: 0.9rem; color: #6b7280; margin-bottom: 4px; }}
        .log-action, .termin-name {{ font-weight: bold; color: #1e40af; }}
        .termin-name {{ color: #7c3aed; }}
        .log-details, .termin-details {{ margin-top: 8px; color: #4b5563; line-height: 1.5; }}
        .empty {{ color: #9ca3af; font-style: italic; }}
        footer {{ text-align: center; margin-top: 50px; color: #6b7280; font-size: 0.9rem; border-top: 1px solid #e5e7eb; padding-top: 20px; }}
        @media (max-width: 768px) {{ .container {{ padding: 15px; }} h1 {{ font-size: 2rem; }} .stat-card {{ min-width: 100%; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐝 Bienenvölker Dashboard</h1>
            <div class="subtitle">Aktuelle Übersicht aller Völker & nächste Termine – Stand {now}</div>
        </header>
        
        <div class="stats">
            <div class="stat-card"><h3>Anzahl Völker</h3><div class="stat-value">{len(voelker)}</div></div>
            <div class="stat-card"><h3>Aktive Völker</h3><div class="stat-value">{active_volks}</div></div>
            <div class="stat-card"><h3>Protokolleinträge</h3><div class="stat-value">{total_logs}</div></div>
            <div class="stat-card"><h3>Geplante Termine</h3><div class="stat-value">{len(cronjobs)}</div></div>
        </div>
        
        <div class="table-container">
            <h2>📊 Volksübersicht</h2>
            <table>
                <thead><tr><th>ID</th><th>Name</th><th>Gewicht (aktuell)</th><th>Letzte Fütterung</th><th>Letzte Varroa‑Behandlung</th><th>Besondere Hinweise</th></tr></thead>
                <tbody>
"""
    for volk_id, volk in voelker.items():
        weight, weight_date = extract_latest_weight(volk.get("logs", []))
        weight_str = f"{weight} kg" if weight else "–"
        if weight_date:
            weight_str += f" ({weight_date})"
        last_feed = volk.get("letzte_fütterung", "") or "–"
        last_varroa = volk.get("letzte_varroa_behandlung", "–")
        notes = volk.get("besondere_hinweise", "")
        html += f"""
                    <tr>
                        <td><span class="volk-id">{volk_id}</span></td>
                        <td><span class="volk-name">{volk.get('name', '')}</span><br><small>{volk.get('standort', '')}</small></td>
                        <td>{weight_str}</td>
                        <td>{last_feed}</td>
                        <td>{last_varroa}</td>
                        <td>{notes}</td>
                    </tr>"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="termine-container">
            <h2>📅 Nächste Termine</h2>
"""
    if cronjobs:
        html += """<div class="termine-section"><h3>🕐 Geplante Aufgaben</h3>"""
        for job in cronjobs:
            task = format_task_description(job)
            schedule = format_cron_schedule(job)
            next_run = format_next_run(job)
            html += f"""
                <div class="termin">
                    <div class="termin-time">{next_run}</div>
                    <div class="termin-name">{task}</div>
                    <div class="termin-details"><strong>Wiederholung:</strong> {schedule}</div>
                </div>"""
        html += """</div>"""
    else:
        html += """<div class="termine-section"><p class="empty">Keine geplanten Termine gefunden.</p></div>"""
    
    html += """
        </div>
        
        <div class="log-container">
            <h2>📝 Neueste Protokolleinträge</h2>
"""
    for volk_id, volk in voelker.items():
        logs = volk.get("logs", [])
        latest_logs = extract_latest_logs(logs, limit=3)
        if not latest_logs:
            continue
        html += f"""<div class="log-section"><h3>{volk.get('name', '')} <span class="volk-id">{volk_id}</span></h3>"""
        for log in latest_logs:
            ts = log.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    ts_display = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    ts_display = ts[:16].replace('T', ' ')
            else:
                ts_display = "–"
            action = log.get("aktion", "")
            details = log.get("details", "")
            menge = log.get("menge", "")
            html += f"""
                <div class="log-entry">
                    <div class="log-time">{ts_display}</div>
                    <div class="log-action">{action} {menge}</div>
                    <div class="log-details">{details}</div>
                </div>"""
        html += """</div>"""
    
    html += """
        </div>
        <footer>
            <p>Erstellt mit dem Imker‑Begleiter Skill | Datenquelle: <code>voelker.json</code> & Terminplanung</p>
            <p>Dashboard wird bei jeder Änderung aktualisiert. Speichern Sie diese HTML‑Datei lokal, um sie offline zu nutzen.</p>
        </footer>
    </div>
</body>
</html>"""
    return html

def main():
    voelker = load_voelker()
    if not voelker:
        print("Keine Volksdaten gefunden.")
        return
    
    cronjobs = []
    if os.path.exists(CRON_CACHE):
        with open(CRON_CACHE, "r", encoding="utf-8") as f:
            data = json.load(f)
        jobs = data.get("jobs", [])
        for job in jobs:
            if not job.get("enabled", True):
                continue
            name = job.get("name", "")
            delivery = job.get("delivery", {})
            to = delivery.get("to", "")
            if to == "6882251060" or name.startswith("imker-") or "varroa" in name:
                cronjobs.append(job)
        print(f"✅ {len(cronjobs)} relevante Termine aus Cache geladen.")
    else:
        print("⚠️ Kein Cron‑Cache vorhanden.")
    
    html_content = generate_html(voelker, cronjobs)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(WORKSPACE_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Dashboard erstellt: {OUTPUT_HTML} & {WORKSPACE_HTML}")
    print(f"   Enthält {len(voelker)} Völker und {len(cronjobs)} Termine.")

if __name__ == "__main__":
    main()