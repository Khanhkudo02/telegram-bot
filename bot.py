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
import requests

# ================= CONFIG =================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ================= DATABASE =================
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

file_memory = {}

# ================= WEATHER =================
def get_weather(city="Ho Chi Minh"):

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=vi"

        data = requests.get(url).json()

        if "main" not in data:
            return "❌ Không lấy được thời tiết."

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"]

        return (
            f"🌤 {city}\n"
            f"🌡 Nhiệt độ: {temp}°C\n"
            f"💧 Độ ẩm: {humidity}%\n"
            f"☁️ {desc}"
        )

    except Exception as e:
        print("Weather error:", e)
        return "❌ Lỗi thời tiết."

# ================= SEARCH =================
def search_web(query):

    try:
        text = ""
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return "❌ Không tìm thấy."

        for r in results:
            text += f"{r['title']}\n{r['body']}\n\n"

        return text.strip()

    except Exception as e:
        print("Search error:", e)
        return "❌ Lỗi tìm kiếm."

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "🤖 AI BOT PRO\n\n"
        "💬 Chat AI\n"
        "🌤 Thời tiết\n"
        "🌐 Tìm kiếm\n"
        "📄 Đọc file\n"
        "🎤 Voice"
    )

# ================= FILE =================
@bot.message_handler(content_types=['document'])
def read_file(message):

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        filename = message.document.file_name

        with open(filename, "wb") as f:
            f.write(downloaded)

        text = ""

        if filename.endswith(".pdf"):
            with pdfplumber.open(filename) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"

        elif filename.endswith(".xlsx"):
            df = pd.read_excel(filename)
            text = df.to_string()

        elif filename.endswith(".docx"):
            doc = Document(filename)
            for para in doc.paragraphs:
                text += para.text + "\n"

        file_memory[message.chat.id] = text[:12000]

        bot.reply_to(message, "📄 Đã đọc file. Hãy hỏi nội dung.")

    except Exception as e:
        print(e)
        bot.reply_to(message, "❌ Không đọc được file.")

# ================= CHAT =================
@bot.message_handler(func=lambda message: True)
def chat(message):

    try:
        user_id = message.chat.id
        text = message.text.lower()

        # ===== WEATHER =====
        if "thời tiết" in text:
            bot.reply_to(message, get_weather())
            return

        # ===== SEARCH =====
        if any(x in text for x in ["tin tức", "giá vàng", "bitcoin", "usd"]):
            result = search_web(message.text)
            bot.reply_to(message, "🌐 " + result)
            return

        # ===== SAVE HISTORY =====
        cursor.execute(
            "INSERT INTO history VALUES(?,?,?)",
            (user_id, "user", message.text)
        )
        conn.commit()

        cursor.execute(
            "SELECT role,content FROM history WHERE user_id=? ORDER BY rowid DESC LIMIT 10",
            (user_id,)
        )

        history = cursor.fetchall()[::-1]

        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là AI trợ lý thông minh.\n"
                    "Nếu có nội dung file thì dùng để trả lời.\n"
                    "Luôn trả lời bằng tiếng Việt."
                )
            }
        ]

        if user_id in file_memory:
            messages.append({
                "role": "system",
                "content": "Nội dung file:\n\n" + file_memory[user_id]
            })

        for role, content in history:
            messages.append({
                "role": role,
                "content": content
            })

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )

        reply = response.choices[0].message.content

        cursor.execute(
            "INSERT INTO history VALUES(?,?,?)",
            (user_id, "assistant", reply)
        )
        conn.commit()

        bot.reply_to(message, reply)

        asyncio.run(send_voice(reply, user_id))

    except Exception as e:
        print(e)
        bot.reply_to(message, "❌ Bot lỗi.")

# ================= VOICE =================
async def send_voice(text, chat_id):

    try:
        communicate = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural")
        await communicate.save("voice.mp3")

        with open("voice.mp3", "rb") as v:
            bot.send_voice(chat_id, v)

    except:
        pass

# ================= RUN =================
print("Bot running...")
bot.infinity_polling()