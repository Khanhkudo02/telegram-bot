import pytesseract
from PIL import Image
import sqlite3

# 👉 FIX ĐƯỜNG DẪN (QUAN TRỌNG)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

def handle_image(bot, message):
    try:
        # tải ảnh
        file = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file.file_path)

        with open("img.jpg", "wb") as f:
            f.write(data)

        # đọc ảnh
        img = Image.open("img.jpg")

        # 👉 CHỈ DÙNG ENG (Railway không có tiếng Việt)
        text = pytesseract.image_to_string(img, lang="eng")

        text = text.strip()

        if not text:
            bot.reply_to(
                message,
                "❌ Không đọc được chữ.\n👉 Gửi ảnh rõ hơn hoặc gửi file (📎)"
            )
            return

        # lưu DB
        cursor.execute("DELETE FROM files WHERE user_id=?", (message.chat.id,))
        cursor.execute("INSERT INTO files VALUES(?,?)", (message.chat.id, text[:12000]))
        conn.commit()

        bot.reply_to(message, f"📸 OCR OK:\n\n{text[:200]}")

    except Exception as e:
        print("OCR ERROR:", e)
        bot.reply_to(message, "❌ OCR lỗi")