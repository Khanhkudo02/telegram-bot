import os
import requests

API_KEY = os.getenv("OPENAI_API_KEY")

def voice_to_text(path):
    try:
        url = "https://api.openai.com/v1/audio/transcriptions"

        headers = {"Authorization": f"Bearer {API_KEY}"}
        files = {
            "file": open(path, "rb"),
            "model": (None, "whisper-1")
        }

        res = requests.post(url, headers=headers, files=files)
        return res.json().get("text", "❌ lỗi voice")

    except Exception as e:
        print(e)
        return "❌ lỗi voice"