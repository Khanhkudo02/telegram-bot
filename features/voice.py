import edge_tts
import asyncio

async def _voice(text, chat_id, bot):
    communicate = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural")
    await communicate.save("voice.mp3")

    with open("voice.mp3", "rb") as v:
        bot.send_voice(chat_id, v)

def send_voice(text, chat_id, bot):
    try:
        asyncio.run(_voice(text, chat_id, bot))
    except:
        pass
