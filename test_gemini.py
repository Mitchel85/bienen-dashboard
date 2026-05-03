import subprocess
import json

def test_model():
    print("Testing Gemini 3.1 Pro Preview...")
    try:
        result = subprocess.run(
            ["openclaw", "chat", "--model", "google/gemini-3.1-pro-preview", "--message", "Reply exactly with: 'Gemini 3.1 Pro is ready.'"],
            capture_output=True,
            text=True,
            timeout=30
        )
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
    except Exception as e:
        print(f"Error: {e}")

test_model()
