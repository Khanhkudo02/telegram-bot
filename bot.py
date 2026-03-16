import os
import telebot
import requests
from urllib.parse import quote
from openai import OpenAI
from gtts import gTTS

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

chat_history = {}

# START
@bot.message_handler(commands=['start'])
def start(message):

    bot.reply_to(
        message,
        "🤖 AI Bot đã sẵn sàng!\n\n"
        "Tính năng:\n"
        "💬 Chat AI\n"
        "🖼 /image tạo ảnh\n"
        "🎤 gửi voice\n"
        "📄 gửi file để đọc\n"
    )

# IMAGE
@bot.message_handler(commands=['image'])
def image(message):

    prompt = message.text.replace("/image", "").strip()

    if prompt == "":
        bot.reply_to(message, "Ví dụ:\n/image con mèo phi hành gia")
        return

    bot.send_message(message.chat.id, "🎨 Đang tạo ảnh...")

    prompt = quote(prompt)

    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024"

    bot.send_photo(message.chat.id, url)

# VOICE INPUT
@bot.message_handler(content_types=['voice'])
def voice(message):

    bot.reply_to(message, "🎤 Đã nhận voice. Tính năng này đang nâng cấp...")

# FILE
@bot.message_handler(content_types=['document'])
def file_handler(message):

    bot.reply_to(message, "📄 Đã nhận file. Bot sẽ đọc file trong bản nâng cấp tiếp theo.")

# CHAT AI
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
                {
                    "role": "system",
                    "content": "Bạn là trợ lý AI thông minh, trả lời ngắn gọn bằng tiếng Việt."
                }
            ] + chat_history[user_id]
        )

        reply = response.choices[0].message.content

        chat_history[user_id].append(
            {"role": "assistant", "content": reply}
        )

        bot.reply_to(message, reply)

        # VOICE OUTPUT
        try:

            tts = gTTS(reply, lang="vi")

            tts.save("voice.mp3")

            with open("voice.mp3", "rb") as voice:

                bot.send_voice(message.chat.id, voice)

        except:
            pass

    except Exception as e:

        print(e)

        bot.reply_to(message, "Bot đang gặp lỗi.")

bot.infinity_polling()