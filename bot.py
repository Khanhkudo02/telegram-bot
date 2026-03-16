import telebot
import os
from openai import OpenAI

BOT_TOKEN = "8668169502:AAEL5CWwL29nFRRx6gXJGfZ86YcYs7BALsw"
client = OpenAI(api_key=os.getenv("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"))

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
