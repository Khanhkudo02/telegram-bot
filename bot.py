import os
import telebot
import requests
import sqlite3
import pdfplumber
import pandas as pd
from duckduckgo_search import DDGS
from urllib.parse import quote
from openai import OpenAI
import edge_tts
import asyncio

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# =================
# MEMORY DATABASE
# =================

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

# =================
# START
# =================

@bot.message_handler(commands=['start'])
def start(message):

    bot.reply_to(
        message,
        "🤖 AI BOT ULTRA\n\n"
        "Commands:\n"
        "/image tạo ảnh AI\n"
        "/search tìm internet\n"
        "gửi voice\n"
        "gửi ảnh\n"
        "gửi file PDF/Word/Excel\n"
    )

# =================
# IMAGE AI
# =================

@bot.message_handler(commands=['image'])
def image(message):

    prompt = message.text.replace("/image","").strip()

    if prompt == "":
        bot.reply_to(message,"Ví dụ:\n/image cyberpunk samurai")
        return

    bot.send_message(message.chat.id,"🎨 Đang tạo ảnh...")

    prompt = quote(prompt)

    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024"

    bot.send_photo(message.chat.id,url)

# =================
# INTERNET SEARCH
# =================

@bot.message_handler(commands=['search'])
def search(message):

    query = message.text.replace("/search","").strip()

    if query == "":
        bot.reply_to(message,"Ví dụ:\n/search tin AI mới")
        return

    text=""

    with DDGS() as ddgs:

        results = ddgs.text(query,max_results=5)

        for r in results:

            text += f"{r['title']}\n{r['href']}\n\n"

    bot.reply_to(message,text)

# =================
# FILE READER
# =================

@bot.message_handler(content_types=['document'])
def read_file(message):

    file_info = bot.get_file(message.document.file_id)

    downloaded = bot.download_file(file_info.file_path)

    filename = message.document.file_name

    with open(filename,"wb") as f:
        f.write(downloaded)

    text=""

    if filename.endswith(".pdf"):

        with pdfplumber.open(filename) as pdf:

            for page in pdf.pages:

                t = page.extract_text()

                if t:
                    text += t

    elif filename.endswith(".xlsx"):

        df = pd.read_excel(filename)

        text = df.to_string()

    elif filename.endswith(".docx"):

        text="Word file received"

    text = text[:3000]

    bot.reply_to(message,"📄 Nội dung file:\n\n"+text)

# =================
# IMAGE VISION
# =================

@bot.message_handler(content_types=['photo'])
def vision(message):

    bot.reply_to(message,"👁 Tôi đã nhận ảnh. Vision AI đang phân tích.")

# =================
# VOICE INPUT
# =================

@bot.message_handler(content_types=['voice'])
def voice(message):

    bot.reply_to(message,"🎤 Voice đã nhận (Whisper có thể thêm API).")

# =================
# CHAT AI
# =================

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
            {"role":"system",
             "content":"Bạn là AI thông minh, giúp tìm thông tin internet và trả lời tiếng Việt."}
        ]

        for role,content in history:

            messages.append({"role":role,"content":content})

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=messages
        )

        reply = response.choices[0].message.content

        cursor.execute(
            "INSERT INTO history VALUES(?,?,?)",
            (user_id,"assistant",reply)
        )

        conn.commit()

        bot.reply_to(message,reply)

        asyncio.run(send_voice(reply,message.chat.id))

    except Exception as e:

        print(e)

        bot.reply_to(message,"Bot đang lỗi.")

# =================
# VOICE OUTPUT
# =================

async def send_voice(text,chat_id):

    communicate = edge_tts.Communicate(text,"vi-VN-HoaiMyNeural")

    await communicate.save("voice.mp3")

    with open("voice.mp3","rb") as v:

        bot.send_voice(chat_id,v)

# =================
# RUN
# =================

print("Bot running...")

bot.infinity_polling()