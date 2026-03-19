import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

from PIL import Image
import sqlite3

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

def handle_image(bot, message):
    try:
        file = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file.file_path)

        with open("img.jpg", "wb") as f:
            f.write(data)

        text = pytesseract.image_to_string(Image.open("img.jpg"))

        cursor.execute("DELETE FROM files WHERE user_id=?", (message.chat.id,))
        cursor.execute("INSERT INTO files VALUES(?,?)", (message.chat.id, text[:12000]))
        conn.commit()

        bot.reply_to(message, "📸 Đã đọc ảnh")

    except:
        bot.reply_to(message, "❌ OCR lỗi")