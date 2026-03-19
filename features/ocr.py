import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import sqlite3
import os

# ===== FIX PATH (QUAN TRỌNG) =====
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

def preprocess(img_path):
    img = Image.open(img_path).convert("L")

    # tăng nét
    img = ImageEnhance.Contrast(img).enhance(2)
    img = img.filter(ImageFilter.SHARPEN)

    # phóng to
    w, h = img.size
    img = img.resize((w*2, h*2))

    new_path = "processed.jpg"
    img.save(new_path)

    return new_path


def handle_image(bot, message):
    try:
        file = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file.file_path)

        with open("img.jpg", "wb") as f:
            f.write(data)

        processed = preprocess("img.jpg")

        # ===== OCR =====
        try:
            text = pytesseract.image_to_string(
                Image.open(processed),
                lang="vie+eng",
                config="--psm 6"
            )
        except:
            text = pytesseract.image_to_string(
                Image.open(processed),
                config="--psm 6"
            )

        text = text.strip()

        # ===== CHECK TEXT =====
        if not text:
            bot.reply_to(
                message,
                "❌ Không đọc được chữ.\n💡 Gửi ảnh rõ hơn hoặc gửi file PDF"
            )
            return

        # ===== SAVE DB =====
        cursor.execute("DELETE FROM files WHERE user_id=?", (message.chat.id,))
        cursor.execute("INSERT INTO files VALUES(?,?)", (message.chat.id, text[:12000]))
        conn.commit()

        preview = text[:200] + "..." if len(text) > 200 else text

        bot.reply_to(
            message,
            f"📸 Đã đọc ảnh!\n\n📝 Preview:\n{preview}\n\n💬 Hỏi tôi về nội dung!"
        )

    except Exception as e:
        print("OCR ERROR:", e)
        bot.reply_to(message, "❌ Lỗi OCR")