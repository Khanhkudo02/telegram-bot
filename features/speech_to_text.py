import whisper

# load model (chỉ load 1 lần)
model = whisper.load_model("base")

def voice_to_text(file_path):
    try:
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        print("STT error:", e)
        return "❌ Không nhận diện được giọng nói"
