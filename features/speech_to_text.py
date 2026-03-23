import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def voice_to_text(path):
    if not OPENAI_API_KEY:
        return "❌ Chưa cấu hình OPENAI_API_KEY → không dùng được voice-to-text."

    try:
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        files = {
            "file": ("audio.ogg", open(path, "rb"), "audio/ogg"),
            "model": (None, "whisper-1"),
            "language": (None, "vi")
        }

        res = requests.post(url, headers=headers, files=files, timeout=30)
        res.raise_for_status()
        return res.json().get("text", "❌ Không nhận diện được giọng nói.")

    except Exception as e:
        print(f"WHISPER ERROR: {e}")
        return f"❌ Lỗi voice-to-text: {str(e)[:80]}"