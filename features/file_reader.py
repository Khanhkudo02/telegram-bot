import pdfplumber
import pandas as pd
from docx import Document
import sqlite3
import pytesseract
from PIL import Image
import os

# ===== FIX TESSERACT PATH (Railway) =====
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

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


# ===== OCR FROM IMAGE =====
def ocr_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="eng")
        return text
    except Exception as e:
        print("OCR ERROR:", e)
        return ""


# ===== HANDLE FILE =====
def handle_file(bot, message):

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        filename = message.document.file_name

        # lưu file
        with open(filename, "wb") as f:
            f.write(downloaded)

        text = ""

        # ================= PDF =================
        if filename.lower().endswith(".pdf"):

            with pdfplumber.open(filename) as pdf:

                for page_num, page in enumerate(pdf.pages):

                    try:
                        t = page.extract_text()

                        if t:
                            text += t + "\n"

                    except Exception as e:
                        print(f"PDF PAGE ERROR {page_num}:", e)

            # ===== nếu PDF không có text → dùng OCR =====
            if not text.strip():

                bot.reply_to(
                    message,
                    "📸 PDF dạng scan → đang dùng OCR..."
                )

                try:
                    import fitz  # PyMuPDF

                    doc = fitz.open(filename)

                    for i, page in enumerate(doc):
                        pix = page.get_pixmap()
                        img_path = f"page_{i}.png"
                        pix.save(img_path)

                        text += ocr_image(img_path) + "\n"

                        os.remove(img_path)

                except Exception as e:
                    print("PDF OCR ERROR:", e)
                    bot.reply_to(message, "❌ Không đọc được PDF scan.")
                    return

        # ================= EXCEL =================
        elif filename.lower().endswith(".xlsx"):

            df = pd.read_excel(filename)
            text = df.to_string()

        # ================= WORD =================
        elif filename.lower().endswith(".docx"):

            doc = Document(filename)

            for para in doc.paragraphs:
                text += para.text + "\n"

        else:
            bot.reply_to(message, "❌ File không hỗ trợ.")
            return

        # ===== CLEAN TEXT =====
        text = text.strip()

        if not text:
            bot.reply_to(message, "❌ Không đọc được nội dung.")
            return

        # ===== LIMIT =====
        text = text[:12000]

        # ===== SAVE DATABASE =====
        cursor.execute("DELETE FROM files WHERE user_id=?", (message.chat.id,))
        cursor.execute(
            "INSERT INTO files VALUES(?,?)",
            (message.chat.id, text)
        )
        conn.commit()

        bot.reply_to(
            message,
            "📄 Đã đọc file thành công!\n💬 Hãy hỏi nội dung."
        )

    except Exception as e:
        print("FILE ERROR:", e)
        bot.reply_to(message, "❌ Lỗi đọc file.")