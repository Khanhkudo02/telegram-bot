import os
import telebot
import requests
import sqlite3
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

# DATABASE lưu lịch sử
conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
user_id INTEGER,
role TEXT,
content TEXT
)
""")

conn.commit()

# START
@bot.message_handler(commands=['start'])
def start(message):

    bot.reply_to(
        message,
        "🤖 AI BOT ĐÃ SẴN SÀNG\n\n"
        "Tính năng:\n"
        "💬 Chat AI\n"
        "🖼 /image tạo ảnh\n"
        "🌐 /search tìm internet\n"
        "🎤 gửi voice\n"
    )

# IMAGE
@bot.message_handler(commands=['image'])
def image(message):

    prompt = message.text.replace("/image","").strip()

    if prompt == "":
        bot.reply_to(message,"Ví dụ:\n/image robot tương lai")
        return

    bot.send_message(message.chat.id,"🎨 Đang tạo ảnh...")

    prompt = quote(prompt)

    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024"

    bot.send_photo(message.chat.id,url)

# INTERNET SEARCH
@bot.message_handler(commands=['search'])
def search(message):

    query = message.text.replace("/search","").strip()

    if query == "":
        bot.reply_to(message,"Ví dụ:\n/search tin tức AI")
        return

    url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json"

    data = requests.get(url).json()

    answer = data.get("Abstract")

    if answer == "":
        answer = "Không tìm thấy thông tin."

    bot.reply_to(message,answer)

# VOICE INPUT
@bot.message_handler(content_types=['voice'])
def voice(message):

    bot.reply_to(message,"🎤 Voice đã nhận (tính năng nhận dạng sẽ nâng cấp thêm).")

# CHAT AI
@bot.message_handler(func=lambda message: True)
def chat(message):

    try:

        user_id = message.chat.id

        cursor.execute(
            "INSERT INTO history VALUES(?,?,?)",
            (user_id,"user",message.text)
        )

        conn.commit()

        cursor.execute(
            "SELECT role,content FROM history WHERE user_id=? ORDER BY rowid DESC LIMIT 10",
            (user_id,)
        )

        history = cursor.fetchall()[::-1]

        messages = [
            {
                "role":"system",
                "content":"Bạn là trợ lý AI thông minh, trả lời tiếng Việt."
            }
        ]

        for role,content in history:
            messages.append({"role":role,"content":content})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        reply = response.choices[0].message.content

        cursor.execute(
            "INSERT INTO history VALUES(?,?,?)",
            (user_id,"assistant",reply)
        )

        conn.commit()

        bot.reply_to(message,reply)

        # VOICE OUTPUT
        tts = gTTS(reply,lang="vi")

        tts.save("voice.mp3")

        with open("voice.mp3","rb") as v:

            bot.send_voice(message.chat.id,v)

    except Exception as e:

        print(e)

        bot.reply_to(message,"Bot đang lỗi.")

bot.infinity_polling()