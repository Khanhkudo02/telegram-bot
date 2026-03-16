import telebot
import os
from openai import OpenAI

BOT_TOKEN = "8668169502:AAEL5CWwL29nFRRx6gXJGfZ86YcYs7BALsw"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def chat(message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message.text}]
    )

    reply = response.choices[0].message.content
    bot.reply_to(message, reply)

bot.polling()
