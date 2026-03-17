import os
import telebot
import sqlite3
import pdfplumber
import pandas as pd
from docx import Document
from duckduckgo_search import DDGS
from openai import OpenAI
import edge_tts
import asyncio

# =================
# CONFIG
# =================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# =================
# DATABASE MEMORY
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

# lưu nội dung file
file_memory = {}

# =================
# START
# =================

@bot.message_handler(commands=['start'])
def start(message):

    bot.reply_to(
        message,
        "🤖 AI BOT PRO\n\n"
        "Tính năng:\n"
        "💬 Chat AI\n"
        "🌐 /search tìm internet\n"
        "📄 gửi PDF / Word / Excel để hỏi\n"
        "👁 gửi ảnh\n"
        "🎤 gửi voice"
    )

# =================
# INTERNET SEARCH
# =================

def search_web(query):

    text = ""

    with DDGS() as ddgs:

        results = ddgs.text(query, max_results=3)

        for r in results:
            text += f"{r['title']}\n{r['body']}\n\n"

    return text


@bot.message_handler(commands=['search'])
def search(message):

    query = message.text.replace("/search","").strip()

    if query == "":
        bot.reply_to(message,"Ví dụ:\n/search tin AI mới")
        return

    result = search_web(query)

    bot.reply_to(message,"🌐 Kết quả:\n\n"+result)

# =================
# FILE READER
# =================

@bot.message_handler(content_types=['document'])
def read_file(message):

    try:

        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        filename = message.document.file_name

        with open(filename,"wb") as f:
            f.write(downloaded)

        text = ""

        # PDF
        if filename.endswith(".pdf"):

            with pdfplumber.open(filename) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"

        # Excel
        elif filename.endswith(".xlsx"):

            df = pd.read_excel(filename)
            text = df.to_string()

        # Word
        elif filename.endswith(".docx"):

            doc = Document(filename)
            for para in doc.paragraphs:
                text += para.text + "\n"

        text = text[:12000]

        file_memory[message.chat.id] = text

        bot.reply_to(
            message,
            "📄 Tôi đã đọc file.\nBạn có thể hỏi về nội dung file."
        )

    except Exception as e:

        print(e)
        bot.reply_to(message,"❌ Không đọc được file.")

# =================
# IMAGE
# =================

@bot.message_handler(content_types=['photo'])
def vision(message):

    bot.reply_to(
        message,
        "👁 Tôi đã nhận ảnh (chưa bật Vision AI thật)."
    )

# =================
# VOICE INPUT
# =================

@bot.message_handler(content_types=['voice'])
def voice(message):

    bot.reply_to(
        message,
        "🎤 Tôi đã nhận voice (chưa bật Whisper)."
    )

# =================
# CHAT AI
# =================

@bot.message_handler(func=lambda message: True)
def chat(message):

    try:

        user_id = message.chat.id
        user_text = message.text.lower()

        # ===== AUTO SEARCH =====
        if any(x in user_text for x in ["thời tiết","tin tức","giá vàng","giá usd"]):

            result = search_web(message.text)

            bot.reply_to(message,"🌐 Thông tin:\n\n"+result)
            return

        # ===== SAVE HISTORY =====
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

        # ===== SYSTEM PROMPT =====
        messages = [
        {
        "role":"system",
        "content":(
        "Bạn là AI trợ lý thông minh.\n"
        "Nếu hệ thống cung cấp nội dung file thì đó là file người dùng vừa gửi.\n"
        "Hãy đọc nội dung đó và trả lời câu hỏi dựa trên file.\n"
        "Luôn trả lời bằng tiếng Việt."
        )
        }
        ]

        # ===== FILE MEMORY =====
        if user_id in file_memory:

            messages.append({
                "role":"system",
                "content":"Đây là nội dung file người dùng gửi:\n\n" + file_memory[user_id]
            })

        # ===== HISTORY =====
        for role,content in history:

            messages.append({
                "role":role,
                "content":content
            })

        # ===== AI CALL =====
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )

        reply = response.choices[0].message.content

        # ===== SAVE AI =====
        cursor.execute(
            "INSERT INTO history VALUES(?,?,?)",
            (user_id,"assistant",reply)
        )
        conn.commit()

        bot.reply_to(message,reply)

        # ===== VOICE OUTPUT =====
        asyncio.run(send_voice(reply,message.chat.id))

    except Exception as e:

        print(e)
        bot.reply_to(message,"❌ Bot đang lỗi.")

# =================
# VOICE OUTPUT
# =================

async def send_voice(text,chat_id):

    try:

        communicate = edge_tts.Communicate(
            text,
            "vi-VN-HoaiMyNeural"
        )

        await communicate.save("voice.mp3")

        with open("voice.mp3","rb") as v:
            bot.send_voice(chat_id,v)

    except:
        pass

# =================
# RUN
# =================

print("Bot running...")

bot.infinity_polling()