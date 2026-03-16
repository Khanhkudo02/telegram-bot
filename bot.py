import os
import telebot
import requests
import sqlite3
import pdfplumber
import pandas as pd
from duckduckgo_search import DDGS
from openai import OpenAI
import edge_tts
import asyncio
from docx import Document

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# =================
# FILE MEMORY
# =================

file_memory = {}

# =================
# DATABASE
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
        "🤖 AI BOT\n\n"
        "Chức năng:\n"
        "• Chat AI\n"
        "• /search tìm internet\n"
        "• gửi file PDF / Word / Excel\n"
        "• hỏi về nội dung file\n"
        "• voice trả lời"
    )

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

        doc = Document(filename)

        for para in doc.paragraphs:
            text += para.text + "\n"

    text = text[:5000]

    file_memory[message.chat.id] = text

    bot.reply_to(
        message,
        "📄 File đã đọc xong.\n\nBạn có thể hỏi về nội dung file."
    )

# =================
# IMAGE RECEIVED
# =================

@bot.message_handler(content_types=['photo'])
def vision(message):

    bot.reply_to(message,"👁 Tôi đã nhận ảnh.")

# =================
# VOICE RECEIVED
# =================

@bot.message_handler(content_types=['voice'])
def voice(message):

    bot.reply_to(message,"🎤 Voice đã nhận.")

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
            {
                "role":"system",
                "content":"Bạn là AI thông minh và luôn trả lời bằng tiếng Việt."
            }
        ]

        # thêm nội dung file nếu có
        if user_id in file_memory:

            messages.append({
                "role":"system",
                "content":"Nội dung file:\n"+file_memory[user_id]
            })

        for role,content in history:

            messages.append({
                "role":role,
                "content":content
            })

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