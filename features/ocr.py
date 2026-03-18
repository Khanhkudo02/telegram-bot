import pytesseract
from PIL import Image
import sqlite3

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

def handle_image(bot, message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        with open("image.jpg", "wb") as f:
            f.write(downloaded)

        # ===== OCR =====
        text = pytesseract.image_to_string(Image.open("image.jpg"), lang="vie")

        # ===== SAVE DB =====
        cursor.execute("DELETE FROM files WHERE user_id=?", (message.chat.id,))
        cursor.execute(
            "INSERT INTO files VALUES(?,?)",
            (message.chat.id, text[:12000])
        )
        conn.commit()

        bot.reply_to(message, "📸 Đã đọc ảnh. Hãy hỏi nội dung.")

    except Exception as e:
        print(e)
        bot.reply_to(message, "❌ Không đọc được ảnh.")