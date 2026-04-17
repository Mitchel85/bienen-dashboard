#!/usr/bin/env python3
"""
Generiert ein HTML-Dashboard für die Bienenvölker basierend auf voelker.json.
"""
import json
import os
from datetime import datetime

# Pfade
SKILL_DIR = "/data/.openclaw/workspace/skills/imker-begleiter"
VOELKER_JSON = os.path.join(SKILL_DIR, "data", "voelker.json")
OUTPUT_HTML = "/data/.openclaw/workspace/bienen_dashboard.html"

def load_data():
    """Lädt die Volksdaten."""
    if not os.path.exists(VOELKER_JSON):
        return {}
    with open(VOELKER_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_latest_weight(logs):
    """Extrahiert das neueste Gewicht aus den Logs."""
    weight = None
    weight_date = None
    for log in reversed(logs):  # neueste zuerst
        if log.get("aktion") == "wiegen" and log.get("menge"):
            # Menge wie "42 kg"
            try:
                # Extrahiere Zahl
                parts = log["menge"].split()
                if parts:
                    weight = float(parts[0])
                    weight_date = log["timestamp"][:10]  # YYYY-MM-DD
                    break
            except (ValueError, IndexError):
                pass
    return weight, weight_date

def extract_latest_logs(logs, limit=3):
    """Extrahiert die neuesten Logs (limit)."""
    # Logs sind bereits chronologisch (älteste zuerst).
    # Wir wollen neueste zuerst anzeigen, also umkehren.
    reversed_logs = list(reversed(logs))
    return reversed_logs[:limit]

def generate_html(voelker):
    """Generiert das HTML-Dashboard."""
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienenvölker Dashboard</title>
    <style>
        * {{
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        body {{
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            padding: 30px;
        }}
        header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid #ffcc00;
            padding-bottom: 20px;
        }}
        h1 {{
            color: #d97706;
            margin: 0;
            font-size: 2.5rem;
        }}
        .subtitle {{
            color: #666;
            font-size: 1.1rem;
            margin-top: 8px;
        }}
        .stats {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            flex: 1;
            min-width: 200px;
            background: linear-gradient(135deg, #fef3c7, #fde68a);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        .stat-card h3 {{
            margin-top: 0;
            color: #92400e;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #d97706;
        }}
        .table-container {{
            overflow-x: auto;
            margin-bottom: 40px;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 800px;
        }}
        th {{
            background-color: #f3f4f6;
            text-align: left;
            padding: 16px;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #d1d5db;
        }}
        td {{
            padding: 16px;
            border-bottom: 1px solid #e5e7eb;
            vertical-align: top;
        }}
        tr:hover {{
            background-color: #f9fafb;
        }}
        .volk-name {{
            font-weight: bold;
            color: #1f2937;
        }}
        .volk-id {{
            display: inline-block;
            background: #dbeafe;
            color: #1e40af;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
        }}
        .log-container {{
            margin-top: 50px;
        }}
        .log-section {{
            background: #f8fafc;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 5px solid #10b981;
        }}
        .log-section h3 {{
            margin-top: 0;
            color: #047857;
            display: flex;
            align-items: center;
        }}
        .log-section h3 .volk-id {{
            margin-left: 10px;
        }}
        .log-entry {{
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            border-left: 4px solid #3b82f6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }}
        .log-time {{
            font-size: 0.9rem;
            color: #6b7280;
            margin-bottom: 4px;
        }}
        .log-action {{
            font-weight: bold;
            color: #1e40af;
        }}
        .log-details {{
            margin-top: 8px;
            color: #4b5563;
            line-height: 1.5;
        }}
        .empty {{
            color: #9ca3af;
            font-style: italic;
        }}
        footer {{
            text-align: center;
            margin-top: 50px;
            color: #6b7280;
            font-size: 0.9rem;
            border-top: 1px solid #e5e7eb;
            padding-top: 20px;
        }}
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            h1 {{
                font-size: 2rem;
            }}
            .stat-card {{
                min-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐝 Bienenvölker Dashboard</h1>
            <div class="subtitle">Aktuelle Übersicht aller Völker – Stand {now}</div>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Anzahl Völker</h3>
                <div class="stat-value">{len(voelker)}</div>
            </div>
            <div class="stat-card">
                <h3>Aktive Völker</h3>
                <div class="stat-value">{sum(1 for v in voelker.values() if v.get('logs'))}</div>
            </div>
            <div class="stat-card">
                <h3>Letzte Aktualisierung</h3>
                <div class="stat-value">{now.split()[0]}</div>
            </div>
        </div>
        
        <div class="table-container">
            <h2>📊 Volksübersicht</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Gewicht (aktuell)</th>
                        <th>Letzte Fütterung</th>
                        <th>Letzte Varroa‑Behandlung</th>
                        <th>Besondere Hinweise</th>
                    </tr>
                </thead>
                <tbody>
"""
    for volk_id, volk in voelker.items():
        weight, weight_date = extract_latest_weight(volk.get("logs", []))
        weight_str = f"{weight} kg" if weight else "–"
        if weight_date:
            weight_str += f" ({weight_date})"
        
        last_feed = volk.get("letzte_fütterung", "–")
        last_varroa = volk.get("letzte_varroa_behandlung", "–")
        notes = volk.get("besondere_hinweise", "")
        
        html += f"""
                    <tr>
                        <td><span class="volk-id">{volk_id}</span></td>
                        <td><span class="volk-name">{volk.get('name', '')}</span><br>
                            <small>{volk.get('standort', '')}</small></td>
                        <td>{weight_str}</td>
                        <td>{last_feed}</td>
                        <td>{last_varroa}</td>
                        <td>{notes}</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="log-container">
            <h2>📝 Neueste Protokolleinträge</h2>
"""
    for volk_id, volk in voelker.items():
        logs = volk.get("logs", [])
        latest_logs = extract_latest_logs(logs, limit=3)
        if not latest_logs:
            continue
        
        html += f"""
            <div class="log-section">
                <h3>{volk.get('name', '')} <span class="volk-id">{volk_id}</span></h3>
"""
        for log in latest_logs:
            ts = log.get("timestamp", "")
            if ts:
                # UTC zu lokaler Zeit umwandeln (einfach nur Datum/Zeit anzeigen)
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
            transkript = log.get("transkript", "")
            
            html += f"""
                <div class="log-entry">
                    <div class="log-time">{ts_display}</div>
                    <div class="log-action">{action} {menge}</div>
                    <div class="log-details">{details}</div>
"""
            if transkript and transkript != "Bilder Volk nur. 1 (rot)" and transkript != "Bilder Volk 2 (grün)":
                html += f"""<div class="log-details"><em>🗣️ {transkript[:100]}{'…' if len(transkript) > 100 else ''}</em></div>"""
            html += """
                </div>
"""
        html += """
            </div>
"""
    
    html += """
        </div>
        
        <footer>
            <p>Erstellt mit dem Imker‑Begleiter Skill | Datenquelle: <code>voelker.json</code></p>
            <p>Dashboard wird bei jeder Änderung aktualisiert. Speichern Sie diese HTML‑Datei lokal, um sie offline zu nutzen.</p>
        </footer>
    </div>
</body>
</html>
"""
    return html

def main():
    voelker = load_data()
    if not voelker:
        print("Keine Volksdaten gefunden.")
        return
    
    html_content = generate_html(voelker)
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Dashboard erstellt: {OUTPUT_HTML}")
    print(f"   Enthält {len(voelker)} Völker mit den neuesten Logs.")

if __name__ == "__main__":
    main()