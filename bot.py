import os
import telebot

from features.weather import get_weather
from features.search import search_web
from features.chat_ai import ask_ai
from features.file_reader import handle_file
from features.voice import send_voice

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 AI BOT PRO")

@bot.message_handler(content_types=['document'])
def file_handler(message):
    handle_file(bot, message)

@bot.message_handler(func=lambda message: True)
def chat(message):

    text = message.text.lower()

    if "thời tiết" in text:
        bot.reply_to(message, get_weather())
        return

    if any(x in text for x in ["tin tức", "bitcoin", "usd", "giá vàng"]):
        bot.reply_to(message, search_web(message.text))
        return

    reply = ask_ai(message.text, message.chat.id)
    bot.reply_to(message, reply)

    send_voice(reply, message.chat.id, bot)

print("Bot running...")
bot.infinity_polling()