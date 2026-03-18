import pdfplumber
import pandas as pd
from docx import Document
import sqlite3

# ===== DATABASE =====
conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS files(
    user_id INTEGER,
    content TEXT
)
""")
conn.commit()


def handle_file(bot, message):

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        filename = message.document.file_name

        with open(filename, "wb") as f:
            f.write(downloaded)

        text = ""

        # ===== READ FILE =====
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

        # ===== SAVE TO DATABASE (FIX QUAN TRỌNG) =====
        cursor.execute("DELETE FROM files WHERE user_id=?", (message.chat.id,))
        cursor.execute(
            "INSERT INTO files VALUES(?,?)",
            (message.chat.id, text[:12000])
        )
        conn.commit()

        bot.reply_to(message, "📄 Đã đọc file. Hãy hỏi nội dung.")

    except Exception as e:
        print(e)
        bot.reply_to(message, "❌ Không đọc được file.")