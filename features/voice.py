import edge_tts
import asyncio

async def _run(text, chat_id, bot):
    tts = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural")
    await tts.save("v.mp3")

    with open("v.mp3", "rb") as f:
        bot.send_voice(chat_id, f)

def send_voice(text, chat_id, bot):
    try:
        asyncio.run(_run(text[:300], chat_id, bot))
    except:
        pass