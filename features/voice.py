import edge_tts
import asyncio
import os

async def _generate_voice(text, output_file):
    communicate = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural")
    await communicate.save(output_file)

def send_voice(text, chat_id, bot):
    try:
        output_file = "voice_reply.mp3"
        asyncio.run(_generate_voice(text[:280], output_file))  # giới hạn độ dài

        with open(output_file, "rb") as f:
            bot.send_voice(chat_id, f, timeout=20)

        os.remove(output_file)
    except Exception as e:
        print(f"VOICE REPLY ERROR: {e}")
        # không gửi thông báo lỗi để tránh spam