#!/usr/bin/env python3
"""
Verarbeitet das Bienen‑Transkript und fügt Log‑Einträge hinzu.
"""
import sys
sys.path.insert(0, '/data/.openclaw/workspace/skills/imker-begleiter/scripts')
from volk_db import add_log

transcript = """Jetzt geht es um die Bienen. Die Bienenstöcke müssen nicht gefüttert werden, weil direkt neben uns jetzt die ganzen Kirschbäume blühen. Also die Fütterung ist nicht notwendig. In zwei Tagen die Varroa-Kontrolle. Und jetzt noch ein wichtiger Hinweis. Ich brauche keine Benachrichtigung darüber, dass ein Cronjob richtig läuft. Ich brauche lediglich dann direkt den Schwarmalarm, wenn es soweit ist."""

# Für jedes Volk (1,2,3) einen Log‑Eintrag hinzufügen
for volk_id in ["1", "2", "3"]:
    log = add_log(
        volk_id=volk_id,
        aktion="kontrollieren",
        menge="",
        details="Keine Fütterung nötig wegen Kirschblüte. Varroa‑Kontrolle in 2 Tagen (19.04.).",
        transkript=""  # Transkript nicht speichern (User‑Wunsch)
    )
    print(f"✅ Log für Volk {volk_id} hinzugefügt: {log['timestamp']}")

print("🎯 Fertig.")