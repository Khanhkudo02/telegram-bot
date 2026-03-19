import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import sqlite3

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()


def preprocess_image(path):
    """Tăng chất lượng ảnh trước khi OCR"""
    img = Image.open(path).convert("L")          # Grayscale

    # Tăng độ tương phản
    img = ImageEnhance.Contrast(img).enhance(2.0)

    # Sharpen để chữ rõ hơn
    img = img.filter(ImageFilter.SHARPEN)

    # Scale lên 2x (Tesseract đọc tốt hơn với ảnh lớn)
    w, h = img.size
    img = img.resize((w * 2, h * 2), Image.LANCZOS)

    processed_path = "image_processed.jpg"
    img.save(processed_path)
    return processed_path


def handle_image(bot, message):
    try:
        # Lấy ảnh chất lượng cao nhất
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)

        with open("image.jpg", "wb") as f:
            f.write(downloaded)

        # Tiền xử lý ảnh
        processed = preprocess_image("image.jpg")

        # Thử OCR tiếng Việt + Anh trước
        try:
            text = pytesseract.image_to_string(
                Image.open(processed),
                lang="vie+eng",
                config="--psm 6"   # Assume uniform block of text
            )
        except Exception:
            # Fallback: chỉ dùng eng nếu không cài lang vie
            text = pytesseract.image_to_string(
                Image.open(processed),
                config="--psm 6"
            )

        text = text.strip()

        if not text:
            bot.reply_to(
                message,
                "❌ Không đọc được chữ trong ảnh.\n"
                "💡 *Gợi ý:* Gửi file ảnh thay vì ảnh thường để giữ chất lượng.",
                parse_mode="Markdown"
            )
            return

        # Lưu vào DB
        cursor.execute("DELETE FROM files WHERE user_id=?", (message.chat.id,))
        cursor.execute(
            "INSERT INTO files VALUES(?,?)",
            (message.chat.id, text[:12000])
        )
        conn.commit()

        # Preview 200 ký tự đầu để user biết đã đọc đúng
        preview = text[:200] + ("..." if len(text) > 200 else "")
        bot.reply_to(
            message,
            f"📸 *Đã đọc ảnh thành công!*\n\n"
            f"📝 *Preview:*\n`{preview}`\n\n"
            f"💬 Hãy hỏi nội dung ảnh!",
            parse_mode="Markdown"
        )

    except Exception as e:
        print(f"[OCR ERROR] {e}")
        bot.reply_to(message, "❌ Lỗi OCR.")