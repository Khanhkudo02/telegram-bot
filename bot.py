import os
import telebot
from openai import OpenAI

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Xin chào! Tôi là bot AI 🤖")

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": message.text}
    ]
)

        reply = response.choices[0].message.content
        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, "Bot đang gặp lỗi.")

bot.infinity_polling()