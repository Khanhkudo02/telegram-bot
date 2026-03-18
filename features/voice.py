import edge_tts
import asyncio

async def _voice(text, chat_id, bot):
    communicate = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural")
    await communicate.save("voice.mp3")

    with open("voice.mp3", "rb") as v:
        bot.send_voice(chat_id, v)

def send_voice(text, chat_id, bot):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_voice(text[:500], chat_id, bot))
        loop.close()
    except Exception as e:
        print(e)