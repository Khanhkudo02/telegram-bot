import os
import sqlite3
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS history(user_id, role, content)")
cursor.execute("CREATE TABLE IF NOT EXISTS files(user_id, content)")
conn.commit()

def ask_ai(text, user_id):

    cursor.execute("INSERT INTO history VALUES(?,?,?)", (user_id, "user", text))
    conn.commit()

    cursor.execute("SELECT role,content FROM history WHERE user_id=? ORDER BY rowid DESC LIMIT 10", (user_id,))
    history = cursor.fetchall()[::-1]

    messages = [{
        "role": "system",
        "content": "Bạn là AI thông minh, trả lời tiếng Việt."
    }]

    # file context
    cursor.execute("SELECT content FROM files WHERE user_id=?", (user_id,))
    file_data = cursor.fetchone()

    if file_data:
        messages.append({"role": "system", "content": file_data[0]})

    for role, content in history:
        messages.append({"role": role, "content": content})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    reply = response.choices[0].message.content

    cursor.execute("INSERT INTO history VALUES(?,?,?)", (user_id, "assistant", reply))
    conn.commit()

    return reply