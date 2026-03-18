import os
import telebot

from features.weather import get_weather
from features.search import search_web
from features.chat_ai import ask_ai
from features.file_reader import handle_file
from features.voice import send_voice
from features.menu import main_menu   # 👈 thêm dòng này

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🤖 AI BOT PRO\n\nChọn chức năng bên dưới 👇",
        reply_markup=main_menu()
    )

# ===== FILE =====
@bot.message_handler(content_types=['document'])
def file_handler(message):
    handle_file(bot, message)

# ===== CHAT =====
@bot.message_handler(func=lambda message: True)
def chat(message):

    text = message.text

    # ===== MENU BUTTON =====
    if text == "🌤 Thời tiết":
        bot.reply_to(message, get_weather())
        return

    if text == "🌐 Tìm kiếm":
        bot.reply_to(message, "🔎 Nhập nội dung cần tìm:")
        return

    if text == "🤖 Chat AI":
        bot.reply_to(message, "💬 Hãy hỏi tôi bất cứ điều gì!")
        return

    if text == "📄 Đọc file":
        bot.reply_to(message, "📎 Gửi file cho tôi.")
        return

    if text == "🎤 Voice":
        bot.reply_to(message, "🎤 Tôi sẽ đọc nội dung bạn gửi.")
        return

    # ===== LOGIC CŨ =====
    text_lower = text.lower()

    if "thời tiết" in text_lower:
        bot.reply_to(message, get_weather())
        return

    if any(x in text_lower for x in ["tin tức", "bitcoin", "usd", "giá vàng"]):
        bot.reply_to(message, search_web(text))
        return

    reply = ask_ai(text, message.chat.id)
    bot.reply_to(message, reply)

    send_voice(reply, message.chat.id, bot)

# ===== RUN =====
print("Bot running...")
bot.infinity_polling()