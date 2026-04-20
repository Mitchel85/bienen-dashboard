#!/usr/bin/env python3
"""
OCR-Skript für Bildanalyse in OpenClaw.
Verwendet Tesseract OCR, um Text aus Bildern zu extrahieren.
"""

import sys
import subprocess
import tempfile
import os
from pathlib import Path

def extract_text(image_path: str, language: str = "deu") -> str:
    """
    Extrahiert Text aus einem Bild mit Tesseract OCR.
    """
    # Prüfe, ob Tesseract installiert ist
    if not shutil.which("tesseract"):
        raise RuntimeError("Tesseract OCR ist nicht installiert. Bitte installiere tesseract-ocr und tesseract-ocr-deu.")
    
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        txt_path = tmp.name
    
    try:
        # Tesseract aufrufen
        cmd = ["tesseract", image_path, txt_path[:-4], "-l", language]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Tesseract fehlgeschlagen: {result.stderr}")
        
        # Ausgabedatei lesen
        output_file = txt_path[:-4] + ".txt"
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                text = f.read().strip()
            os.unlink(output_file)
        else:
            text = ""
        
        return text
    finally:
        if os.path.exists(txt_path):
            os.unlink(txt_path)

if __name__ == "__main__":
    import shutil
    if len(sys.argv) < 2:
        print("Usage: python3 ocr_image.py <image_path> [language]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "deu"
    
    if not os.path.exists(image_path):
        print(f"Fehler: Bilddatei {image_path} existiert nicht.")
        sys.exit(1)
    
    try:
        text = extract_text(image_path, lang)
        if text:
            print(text)
        else:
            print("(Kein Text erkannt)")
    except Exception as e:
        print(f"Fehler: {e}")
        sys.exit(1)