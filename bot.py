import os
import telebot
from openai import OpenAI

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("Bot starting...")

bot = telebot.TeleBot(BOT_TOKEN)

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Xin chào! Tôi là bot AI 🤖")

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": message.text}
    ]
)

        reply = response.choices[0].message.content
        bot.reply_to(message, reply)

    except Exception as e:
        print("ERROR:", e)
        bot.reply_to(message, "Bot đang gặp lỗi.")

bot.infinity_polling()