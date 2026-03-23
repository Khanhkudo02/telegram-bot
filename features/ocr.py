import pytesseract
from PIL import Image
import sqlite3
import os

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

def handle_image(bot, message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)

        img_path = "temp_ocr.jpg"
        with open(img_path, "wb") as f:
            f.write(data)

        img = Image.open(img_path)
        text = pytesseract.image_to_string(img, lang="eng+vie").strip()

        os.remove(img_path)

        if not text:
            bot.reply_to(
                message,
                "❌ Không nhận diện được chữ trong ảnh.\nHãy gửi ảnh rõ nét, chữ đen nền trắng tốt hơn."
            )
            return

        # Lưu vào DB
        cursor.execute("INSERT OR REPLACE INTO files (user_id, content) VALUES (?, ?)",
                       (message.chat.id, text[:12000]))
        conn.commit()

        preview = text[:300] + "..." if len(text) > 300 else text
        bot.reply_to(message, f"📸 OCR thành công:\n\n{preview}\n\n💬 Hỏi tôi về nội dung ảnh nhé!")

    except Exception as e:
        print(f"OCR ERROR: {e}")
        bot.reply_to(message, "❌ Lỗi OCR. Thử gửi ảnh khác.")