import os
import telebot
import requests
import sqlite3
import pdfplumber
import pandas as pd
import time
import threading
from datetime import datetime
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

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
chat_id INTEGER,
time TEXT,
text TEXT
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
        "/image tạo ảnh\n"
        "/search tìm internet\n"
        "/remind HH:MM nội dung\n"
        "/listremind\n"
        "/delremind id\n"
        "gửi file / voice / ảnh"
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
# REMINDER SET
# =================

@bot.message_handler(commands=['remind'])
def set_reminder(message):

    try:

        parts = message.text.split(" ",2)

        if len(parts) < 3:
            bot.reply_to(message,"Ví dụ:\n/remind 05:15 Dậy học")
            return

        time_str = parts[1]
        text = parts[2]

        cursor.execute(
            "INSERT INTO reminders(chat_id,time,text) VALUES(?,?,?)",
            (message.chat.id,time_str,text)
        )

        conn.commit()

        bot.reply_to(message,f"⏰ Đã đặt nhắc lúc {time_str}")

    except:
        bot.reply_to(message,"Lỗi đặt nhắc.")

# =================
# LIST REMINDER
# =================

@bot.message_handler(commands=['listremind'])
def list_reminders(message):

    cursor.execute(
        "SELECT id,time,text FROM reminders WHERE chat_id=?",
        (message.chat.id,)
    )

    rows = cursor.fetchall()

    if len(rows)==0:
        bot.reply_to(message,"Không có nhắc việc.")
        return

    text="📋 Nhắc việc:\n\n"

    for r in rows:

        text+=f"{r[0]}. {r[1]} - {r[2]}\n"

    bot.reply_to(message,text)

# =================
# DELETE REMINDER
# =================

@bot.message_handler(commands=['delremind'])
def delete_reminder(message):

    try:

        id=int(message.text.split(" ")[1])

        cursor.execute(
            "DELETE FROM reminders WHERE id=?",
            (id,)
        )

        conn.commit()

        bot.reply_to(message,"Đã xoá.")

    except:

        bot.reply_to(message,"Ví dụ:\n/delremind 1")

# =================
# CHECK REMINDER LOOP
# =================

def reminder_loop():

    while True:

        now=datetime.now().strftime("%H:%M")

        cursor.execute("SELECT id,chat_id,time,text FROM reminders")

        rows=cursor.fetchall()

        for r in rows:

            if r[2]==now:

                bot.send_message(
                    r[1],
                    f"⏰ Nhắc nhở:\n{r[3]}"
                )

        time.sleep(60)

threading.Thread(target=reminder_loop).start()

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

    text=text[:3000]

    bot.reply_to(message,"📄 Nội dung file:\n\n"+text)

# =================
# IMAGE VISION
# =================

@bot.message_handler(content_types=['photo'])
def vision(message):

    bot.reply_to(message,"👁 Tôi đã nhận ảnh.")

# =================
# VOICE INPUT
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
            {"role":"system",
             "content":"Bạn là AI thông minh và luôn trả lời bằng tiếng Việt."}
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