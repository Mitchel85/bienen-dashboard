#!/usr/bin/env python3
"""
Generiert ein Bienen-Dashboard als HTML-Datei aus den Völker-Daten.
"""

import json
import os
from datetime import datetime, timedelta
import sys

def load_voelker_data():
    """Lädt die Völker-Daten aus der JSON-Datei."""
    data_path = "/data/.openclaw/workspace/skills/imker-begleiter/data/voelker.json"
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Datei nicht gefunden: {data_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON-Fehler: {e}")
        return None

def analyze_volk_status(volk):
    """Analysiert den Status eines Volks und gibt Handlungsempfehlungen."""
    recommendations = []
    status = "ok"
    
    # Prüfe Varroa-Behandlung
    if volk.get("letzte_varroa_behandlung"):
        try:
            last_treatment = datetime.strptime(volk["letzte_varroa_behandlung"], "%Y-%m-%d")
            days_since = (datetime.now() - last_treatment).days
            if days_since > 90:
                recommendations.append(f"⚠️ Varroa-Behandlung überfällig ({days_since} Tage)")
                status = "warning"
            elif days_since > 60:
                recommendations.append(f"ℹ️ Varroa-Behandlung bald fällig ({days_since} Tage)")
        except ValueError:
            pass
    
    # Prüfe letzte Logs
    logs = volk.get("logs", [])
    if logs:
        try:
            last_log_str = logs[-1]["timestamp"].replace('Z', '+00:00')
            if '+' in last_log_str:
                last_log = datetime.fromisoformat(last_log_str)
            else:
                last_log = datetime.fromisoformat(last_log_str + '+00:00')
            # Beide Zeitstempel auf naive konvertieren für Vergleich
            last_log_naive = last_log.replace(tzinfo=None)
            days_since_log = (datetime.now() - last_log_naive).days
            if days_since_log > 7:
                recommendations.append(f"⚠️ Letzte Kontrolle vor {days_since_log} Tagen")
                status = "warning"
        except (KeyError, ValueError):
            pass
    
    # Prüfe besondere Hinweise
    if "schwach" in volk.get("besondere_hinweise", "").lower():
        recommendations.append("⚠️ Volk ist schwach")
        status = "warning"
    if "schwärmt" in volk.get("besondere_hinweise", "").lower():
        recommendations.append("ℹ️ Schwarmneigung")
    
    return status, recommendations

def generate_dashboard_html(voelker_data):
    """Generiert das HTML-Dashboard."""
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Statistik berechnen
    active_voelker = len([v for k, v in voelker_data.items() if k != 'meta' and v.get('name') != 'Leerer Stock'])
    voelker_with_logs = len([v for k, v in voelker_data.items() if k != 'meta' and v.get('logs')])
    total_logs = sum(len(v.get('logs', [])) for k, v in voelker_data.items() if k != 'meta')
    
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienen-Dashboard | Imker-Begleiter</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #4CAF50;
        }}
        h1 {{
            color: #2E7D32;
            margin-bottom: 10px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .stat-box {{
            background: #E8F5E9;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 10px;
            min-width: 150px;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2E7D32;
        }}
        .volk-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .volk-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: #fff;
        }}
        .volk-header {{
            background: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin: -15px -15px 15px -15px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .status-ok {{ background: #4CAF50; color: white; }}
        .status-warning {{ background: #FF9800; color: white; }}
        .info-row {{
            margin: 8px 0;
            display: flex;
            justify-content: space-between;
        }}
        .recommendations {{
            background: #FFF3E0;
            padding: 10px;
            border-radius: 5px;
            margin-top: 15px;
            border-left: 4px solid #FF9800;
        }}
        .logs {{
            margin-top: 15px;
            font-size: 0.9em;
        }}
        .log-entry {{
            border-bottom: 1px solid #eee;
            padding: 5px 0;
        }}
        .update-time {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }}
        .quality-note {{
            background: #FFF9C4;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin: 20px 0;
            border: 1px solid #FFD54F;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🍯 Bienen-Dashboard</h1>
            <p>Imker-Begleiter | Echtzeit-Überwachung Ihrer Bienenvölker</p>
        </header>
        
        <div class="update-time">
            <strong>Letzte Aktualisierung:</strong> {current_time}
        </div>
        
        <div class="quality-note">
            {voelker_data.get('meta', {}).get('qualitaetshinweis', 'Qualitätsgeprüfter Honig')}
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{active_voelker}</div>
                <div>Aktive Völker</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{voelker_with_logs}</div>
                <div>Völker mit Logs</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{total_logs}</div>
                <div>Log-Einträge</div>
            </div>
        </div>
        
        <div class="volk-grid">
"""
    
    # Völker-Karten generieren
    for volk_id, volk in voelker_data.items():
        if volk_id == 'meta':
            continue
            
        status, recommendations = analyze_volk_status(volk)
        status_class = f"status-{status}"
        status_text = "OK" if status == "ok" else "Achtung"
        
        # Letzte 2 Logs anzeigen
        recent_logs = volk.get('logs', [])[-2:] if volk.get('logs') else []
        
        html += f"""
            <div class="volk-card">
                <div class="volk-header">
                    {volk.get('name', 'Unbenannt')} (Volk #{volk_id})
                    <span class="status-badge {status_class}">{status_text}</span>
                </div>
                
                <div class="info-row">
                    <span>Standort:</span>
                    <span><strong>{volk.get('standort', 'Nicht angegeben')}</strong></span>
                </div>
                <div class="info-row">
                    <span>Rasse:</span>
                    <span>{volk.get('rasse', 'Unbekannt')}</span>
                </div>
                <div class="info-row">
                    <span>Königin:</span>
                    <span>{volk.get('königin_gezeichnet', 'Nicht gezeichnet')}</span>
                </div>
                <div class="info-row">
                    <span>Letzte Varroa-Behandlung:</span>
                    <span>{volk.get('letzte_varroa_behandlung', 'Keine')}</span>
                </div>
                <div class="info-row">
                    <span>Hinweise:</span>
                    <span>{volk.get('besondere_hinweise', 'Keine')}</span>
                </div>
"""
        
        if recommendations:
            html += f"""
                <div class="recommendations">
                    <strong>Handlungsempfehlungen:</strong>
                    <ul style="margin: 5px 0; padding-left: 20px;">
"""
            for rec in recommendations:
                html += f"<li>{rec}</li>"
            html += """
                    </ul>
                </div>
"""
        
        if recent_logs:
            html += """
                <div class="logs">
                    <strong>Aktuelle Aktivitäten:</strong>
"""
            for log in reversed(recent_logs):
                try:
                    ts_str = log['timestamp'].replace('Z', '+00:00')
                    if '+' in ts_str:
                        timestamp = datetime.fromisoformat(ts_str)
                    else:
                        timestamp = datetime.fromisoformat(ts_str + '+00:00')
                    time_str = timestamp.strftime("%d.%m. %H:%M")
                except:
                    time_str = log.get('timestamp', 'Unbekannt')
                
                action_map = {
                    'kontrollieren': '👁️ Kontrolle',
                    'varroa_diagnose': '🔬 Varroa-Diagnose',
                    'wiegen': '⚖️ Wiegen',
                    'foto_analyse': '📸 Foto-Analyse'
                }
                
                action_display = action_map.get(log.get('aktion'), log.get('aktion', 'Aktion'))
                
                html += f"""
                    <div class="log-entry">
                        <div><strong>{time_str}</strong> - {action_display}</div>
                        <div>{log.get('details', '')}</div>
                        {f'<div>Menge: {log.get("menge", "")}</div>' if log.get('menge') else ''}
                    </div>
"""
            html += """
                </div>
"""
        
        html += """
            </div>
"""
    
    html += """
        </div>
        
        <div class="update-time">
            Datenquelle: voelker.json | Generiert am: """ + current_time + """
        </div>
    </div>
</body>
</html>"""
    
    return html

def main():
    """Hauptfunktion."""
    print("🔄 Lade Bienen-Daten...")
    voelker_data = load_voelker_data()
    
    if not voelker_data:
        print("❌ Konnte Daten nicht laden.")
        sys.exit(1)
    
    print("📊 Generiere Dashboard...")
    html = generate_dashboard_html(voelker_data)
    
    # HTML-Datei speichern
    output_path = "/data/.openclaw/workspace/bienen_dashboard.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard generiert: {output_path}")
    print(f"📄 Dateigröße: {len(html)} Bytes")
    
    # Optional: In Datei-URL umwandeln für einfachen Zugriff
    file_url = f"file://{output_path}"
    print(f"🔗 Öffnen mit: {file_url}")

if __name__ == "__main__":
    main()