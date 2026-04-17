#!/usr/bin/env python3
"""
Automatische Veröffentlichung des Bienen‑Dashboards.
Prüft, ob sich die Bienen‑Daten (voelker.json) geändert haben,
generiert ggf. das Dashboard und pusht auf origin/main.
"""
import json
import os
import hashlib
import subprocess
import sys
from datetime import datetime

SKILL_DIR = "/data/.openclaw/workspace/skills/imker-begleiter"
VOELKER_JSON = os.path.join(SKILL_DIR, "data", "voelker.json")
HASH_FILE = "/tmp/dashboard_voelker_hash.txt"
WORKSPACE = "/data/.openclaw/workspace"
DASHBOARD_SCRIPT = os.path.join(WORKSPACE, "generate_bienen_dashboard_v3.py")

def get_file_hash(path):
    """SHA256‑Hash einer Datei berechnen."""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def load_previous_hash():
    """Gespeicherten Hash laden."""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            return f.read().strip()
    return None

def save_current_hash(hash_value):
    """Aktuellen Hash speichern."""
    with open(HASH_FILE, "w") as f:
        f.write(hash_value)

def run_cmd(cmd, cwd=None):
    """Shell‑Befehl ausführen und Ausgabe loggen."""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"stderr: {result.stderr}")
    return result.returncode, result.stdout, result.stderr

def git_status_clean(cwd):
    """Prüfen, ob Git‑Repository clean ist (keine uncommitted changes)."""
    rc, out, err = run_cmd("git status --porcelain", cwd=cwd)
    return rc == 0 and out.strip() == ""

def main():
    print(f"{datetime.now().isoformat()} – Prüfe auf Änderungen in {VOELKER_JSON}")
    
    # 1. Hash der aktuellen Daten
    current_hash = get_file_hash(VOELKER_JSON)
    if current_hash is None:
        print("❌ voelker.json nicht gefunden.")
        return 1
    
    previous_hash = load_previous_hash()
    
    # 2. Falls Hash gleich → nichts tun
    if current_hash == previous_hash:
        print("✅ Keine Änderungen an den Bienen‑Daten.")
        return 0
    
    print("🔄 Bienen‑Daten haben sich geändert. Generiere Dashboard...")
    
    # 3. Dashboard generieren
    if not os.path.exists(DASHBOARD_SCRIPT):
        print(f"❌ Dashboard‑Skript nicht gefunden: {DASHBOARD_SCRIPT}")
        return 1
    
    rc, out, err = run_cmd(f"python3 {DASHBOARD_SCRIPT}", cwd=WORKSPACE)
    if rc != 0:
        print(f"❌ Dashboard‑Generierung fehlgeschlagen: {err}")
        return 1
    
    # 4. Git‑Status prüfen (sollte clean sein)
    if not git_status_clean(WORKSPACE):
        print("⚠️ Git‑Repository ist nicht clean. Führe 'git add .' durch (keine halben Sachen!).")
        rc, out, err = run_cmd("git add .", cwd=WORKSPACE)
        if rc != 0:
            print(f"❌ git add fehlgeschlagen: {err}")
            return 1
        
        # Commit
        commit_msg = f"Auto‑Update Dashboard {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        rc, out, err = run_cmd(f'git commit -m "{commit_msg}"', cwd=WORKSPACE)
        if rc != 0:
            print(f"❌ git commit fehlgeschlagen: {err}")
            return 1
        
        # Push auf origin/main
        rc, out, err = run_cmd("git push origin master:main", cwd=WORKSPACE)
        if rc != 0:
            print(f"❌ git push fehlgeschlagen: {err}")
            return 1
        
        print("✅ Dashboard erfolgreich gepusht (alles committet).")
    else:
        print("ℹ️ Keine Änderungen an index.html (skippe Commit).")
    
    # 5. Hash speichern
    save_current_hash(current_hash)
    print("✅ Hash gespeichert. Nächste Prüfung beim nächsten Lauf.")
    return 0

if __name__ == "__main__":
    sys.exit(main())