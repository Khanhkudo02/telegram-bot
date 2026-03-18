import os
import sqlite3
from openai import OpenAI
from features.file_reader import file_memory  # 👈 FIX QUAN TRỌNG

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
user_id INTEGER,
role TEXT,
content TEXT
)
""")
conn.commit()


def ask_ai(text, user_id):

    # ===== SAVE USER =====
    cursor.execute(
        "INSERT INTO history VALUES(?,?,?)",
        (user_id, "user", text)
    )
    conn.commit()

    # ===== LOAD HISTORY =====
    cursor.execute(
        "SELECT role,content FROM history WHERE user_id=? ORDER BY rowid DESC LIMIT 10",
        (user_id,)
    )

    history = cursor.fetchall()[::-1]

    messages = [
        {
            "role": "system",
            "content": (
                "Bạn là AI trợ lý thông minh.\n"
                "Nếu có nội dung file thì ưu tiên dùng để trả lời.\n"
                "Luôn trả lời bằng tiếng Việt."
            )
        }
    ]

    # ===== 👉 FIX FILE MEMORY Ở ĐÂY =====
    if user_id in file_memory:
        messages.append({
            "role": "system",
            "content": "Nội dung file:\n\n" + file_memory[user_id]
        })

    # ===== HISTORY =====
    for role, content in history:
        messages.append({
            "role": role,
            "content": content
        })

    # ===== AI =====
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    reply = response.choices[0].message.content

    # ===== SAVE BOT =====
    cursor.execute(
        "INSERT INTO history VALUES(?,?,?)",
        (user_id, "assistant", reply)
    )
    conn.commit()

    return reply