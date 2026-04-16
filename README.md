# Bienenvölker Dashboard

Statisches HTML‑Dashboard für die Verwaltung von Bienenvölkern – generiert aus `voelker.json` und Cronjobs.

## 🚀 Live‑Demo

[GitHub Pages](https://mitchel85.github.io/bienen-dashboard/) – nach dem ersten Push aktiv.

## 📁 Dateien

- `bienen_dashboard.html` – Das aktuelle Dashboard (wird automatisch generiert)
- `generate_bienen_dashboard_v3.py` – Generator‑Skript (liest `voelker.json` und Cronjobs)
- `voelker.json` – **Nicht im Repository** (sensible Daten, lokale Speicherung)

## 🔧 Lokale Generierung

```bash
python3 generate_bienen_dashboard_v3.py
```

Das Skript erzeugt `bienen_dashboard.html` im aktuellen Verzeichnis.

## 📅 Automatische Updates (Cron)

```cron
0 7 * * * cd /pfad/zum/workspace && python3 generate_bienen_dashboard_v3.py && cp bienen_dashboard.html /var/www/bienen/
```

## 🐝 Datenquelle

- **Volksdaten**: `skills/imker‑begleiter/data/voelker.json`
- **Cronjobs**: `openclaw cron list --json`

## 📄 Lizenz

MIT – frei nutzbar für private und kommerzielle Zwecke.