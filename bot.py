import os
import telebot
from openai import OpenAI
from gtts import gTTS

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("Bot starting...")

bot = telebot.TeleBot(BOT_TOKEN)

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# lưu lịch sử chat
chat_history = {}

# start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Xin chào! Tôi là bot AI 🤖\n\nBạn có thể:\n- Chat bình thường\n- /image mô tả để tạo ảnh")

# tạo ảnh AI
@bot.message_handler(commands=['image'])
def image(message):
    prompt = message.text.replace("/image", "").strip()

    if prompt == "":
        bot.reply_to(message, "Hãy nhập mô tả ảnh.\nVí dụ:\n/image mèo phi hành gia")
        return

    url = f"https://image.pollinations.ai/prompt/{prompt}"

    bot.send_message(message.chat.id, "🎨 Đang tạo ảnh...")
    bot.send_photo(message.chat.id, url)

# chat AI
@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        user_id = message.chat.id

        if user_id not in chat_history:
            chat_history[user_id] = []

        chat_history[user_id].append(
            {"role": "user", "content": message.text}
        )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý AI thân thiện và luôn trả lời bằng tiếng Việt."}
            ] + chat_history[user_id]
        )

        reply = response.choices[0].message.content

        chat_history[user_id].append(
            {"role": "assistant", "content": reply}
        )

        bot.reply_to(message, reply)

        # tạo voice
        tts = gTTS(reply, lang="vi")
        tts.save("voice.mp3")

        voice = open("voice.mp3", "rb")
        bot.send_voice(message.chat.id, voice)

    except Exception as e:
        print("ERROR:", e)
        bot.reply_to(message, "Bot đang gặp lỗi.")

bot.infinity_polling()