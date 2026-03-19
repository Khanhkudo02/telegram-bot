import pdfplumber
import pandas as pd
from docx import Document
import sqlite3

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

def handle_file(bot, message):
    try:
        file = bot.get_file(message.document.file_id)
        data = bot.download_file(file.file_path)

        name = message.document.file_name

        with open(name, "wb") as f:
            f.write(data)

        text = ""

        if name.endswith(".pdf"):
            with pdfplumber.open(name) as pdf:
                for p in pdf.pages:
                    t = p.extract_text()
                    if t:
                        text += t + "\n"

        elif name.endswith(".docx"):
            doc = Document(name)
            for p in doc.paragraphs:
                text += p.text + "\n"

        elif name.endswith(".xlsx"):
            df = pd.read_excel(name)
            text = df.to_string()

        cursor.execute("DELETE FROM files WHERE user_id=?", (message.chat.id,))
        cursor.execute("INSERT INTO files VALUES(?,?)", (message.chat.id, text[:12000]))
        conn.commit()

        bot.reply_to(message, "📄 Đã đọc file")

    except Exception as e:
        print(e)
        bot.reply_to(message, "❌ Lỗi file")