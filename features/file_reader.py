import pdfplumber
import pandas as pd
from docx import Document
import sqlite3
import pytesseract
from PIL import Image
import os

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

def ocr_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="eng+vie")  # thử cả eng + vie nếu có data
        return text.strip()
    except Exception as e:
        print(f"OCR ERROR: {e}")
        return ""

def handle_file(bot, message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        filename = message.document.file_name.lower()
        file_path = f"temp_{message.chat.id}_{filename}"
        
        with open(file_path, "wb") as f:
            f.write(downloaded)

        text = ""

        if filename.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"

            if not text.strip():  # PDF scan → OCR
                bot.reply_to(message, "📸 Phát hiện PDF dạng ảnh, đang dùng OCR...")
                try:
                    import fitz
                    doc = fitz.open(file_path)
                    for i, page in enumerate(doc):
                        pix = page.get_pixmap(dpi=150)
                        img_path = f"page_{i}.png"
                        pix.save(img_path)
                        text += ocr_image(img_path) + "\n\n"
                        os.remove(img_path)
                    doc.close()
                except Exception as e:
                    print(f"PDF OCR FAIL: {e}")
                    bot.reply_to(message, "❌ Không đọc được PDF scan.")
                    os.remove(file_path)
                    return

        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
            text = df.to_string(index=False)

        elif filename.endswith(".docx"):
            doc = Document(file_path)
            text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())

        else:
            bot.reply_to(message, "❌ Chỉ hỗ trợ: PDF, Word (.docx), Excel (.xlsx)")
            os.remove(file_path)
            return

        text = text.strip()[:15000]  # giới hạn an toàn

        if not text:
            bot.reply_to(message, "❌ Không trích xuất được nội dung từ file.")
            os.remove(file_path)
            return

        # Lưu vào DB (thay thế nếu đã có)
        cursor.execute("INSERT OR REPLACE INTO files (user_id, content) VALUES (?, ?)",
                       (message.chat.id, text))
        conn.commit()

        bot.reply_to(
            message,
            f"📄 Đã đọc file thành công!\n(Độ dài: {len(text)} ký tự)\n\n💬 Bạn có thể hỏi về nội dung file ngay bây giờ."
        )

        os.remove(file_path)

    except Exception as e:
        print(f"FILE HANDLER ERROR: {e}")
        bot.reply_to(message, "❌ Lỗi khi xử lý file. Thử gửi file khác xem sao.")
        if os.path.exists(file_path):
            os.remove(file_path)