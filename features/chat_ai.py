import os
import sqlite3
from openai import OpenAI

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

file_memory = {}

def ask_ai(text, user_id):

    cursor.execute(
        "INSERT INTO history VALUES(?,?,?)",
        (user_id, "user", text)
    )
    conn.commit()

    cursor.execute(
        "SELECT role,content FROM history WHERE user_id=? ORDER BY rowid DESC LIMIT 10",
        (user_id,)
    )

    history = cursor.fetchall()[::-1]

    messages = [{
        "role": "system",
        "content": "Bạn là AI trợ lý thông minh. Luôn trả lời bằng tiếng Việt."
    }]

    if user_id in file_memory:
        messages.append({
            "role": "system",
            "content": "Nội dung file:\n\n" + file_memory[user_id]
        })

    for role, content in history:
        messages.append({
            "role": role,
            "content": content
        })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    reply = response.choices[0].message.content

    cursor.execute(
        "INSERT INTO history VALUES(?,?,?)",
        (user_id, "assistant", reply)
    )
    conn.commit()

    return reply
