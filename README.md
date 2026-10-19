# Bienenvölker Dashboard

Statisches HTML-Dashboard für die Imker-Bienenstöcke (Ludwigsfelde). Kein Build-Schritt nötig.

- **Datenquelle:** `voelker.json` wird zur Laufzeit per `fetch()` geladen — Änderungen an der Datei erscheinen nach einem Reload (über HTTP, z. B. GitHub Pages).
- **Fallback:** Ist `voelker.json` nicht erreichbar (Öffnen per `file://` oder offline), rendert das Dashboard den eingebetteten Datenstand (identisch mit der `voelker.json` im Repo).
- **Skill:** Imker-Begleiter
