import os
import sqlite3
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("❌ Thiếu biến môi trường GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# KẾT NỐI DATABASE
conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

# TẠO BẢNG NẾU CHƯA CÓ
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT,
    content TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    user_id INTEGER PRIMARY KEY,
    content TEXT
)
""")
conn.commit()

def ask_ai(text, user_id):
    try:
        # Lưu tin nhắn người dùng
        cursor.execute(
            "INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, "user", text)
        )
        conn.commit()

        # Lấy lịch sử gần nhất (10 tin nhắn)
        cursor.execute(
            "SELECT role, content FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 10",
            (user_id,)
        )
        history_rows = cursor.fetchall()
        history = history_rows[::-1]  # đảo lại để đúng thứ tự thời gian

        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là trợ lý AI thông minh, trung thực và hữu ích.\n"
                    "Trả lời bằng tiếng Việt tự nhiên, ngắn gọn, rõ ràng.\n"
                    "Nếu có nội dung file được cung cấp → BẮT BUỘC sử dụng để trả lời chính xác.\n"
                    "Không nói 'không có file' nếu file đã được gửi."
                )
            }
        ]

        # Thêm nội dung file nếu có
        cursor.execute("SELECT content FROM files WHERE user_id = ?", (user_id,))
        file_row = cursor.fetchone()
        if file_row and file_row[0]:
            file_content = file_row[0][:14000]  # giới hạn để tránh token quá dài
            messages.append({
                "role": "system",
                "content": f"Nội dung file người dùng vừa gửi (dùng để trả lời):\n\n{file_content}"
            })

        # Thêm lịch sử chat
        for role, content in history:
            messages.append({"role": role, "content": content})

        # Gọi Groq API
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9
        )

        reply = response.choices[0].message.content.strip()

        # Lưu câu trả lời của bot
        cursor.execute(
            "INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, "assistant", reply)
        )
        conn.commit()

        return reply

    except Exception as e:
        print(f"AI ERROR: {str(e)}")
        return f"❌ Lỗi khi gọi AI: {str(e)[:120]}\nThử lại sau vài giây nhé!"