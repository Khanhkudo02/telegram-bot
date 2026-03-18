import os
import telebot

from features.weather import get_weather
from features.search import search_web
from features.chat_ai import ask_ai
from features.file_reader import handle_file
from features.voice import send_voice
from features.menu import main_menu

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

    # ép Telegram hiển thị menu
    bot.send_message(message.chat.id, "👇 Menu sẵn sàng")

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
        bot.send_message(message.chat.id, get_weather(), reply_markup=main_menu())
        return

    if text == "🌐 Tìm kiếm":
        bot.send_message(message.chat.id, "🔎 Nhập nội dung cần tìm:", reply_markup=main_menu())
        return

    if text == "🤖 Chat AI":
        bot.send_message(message.chat.id, "💬 Hãy hỏi tôi bất cứ điều gì!", reply_markup=main_menu())
        return

    if text == "📄 Đọc file":
        bot.send_message(message.chat.id, "📎 Gửi file cho tôi.", reply_markup=main_menu())
        return

    if text == "🎤 Voice":
        bot.send_message(message.chat.id, "🎤 Tôi sẽ đọc nội dung bạn gửi.", reply_markup=main_menu())
        return

    # ===== LOGIC CŨ =====
    text_lower = text.lower()

    if "thời tiết" in text_lower:
        bot.send_message(message.chat.id, get_weather(), reply_markup=main_menu())
        return

    if any(x in text_lower for x in ["tin tức", "bitcoin", "usd", "giá vàng"]):
        bot.send_message(message.chat.id, search_web(text), reply_markup=main_menu())
        return

    # ===== AI =====
    reply = ask_ai(text, message.chat.id)

    bot.send_message(message.chat.id, reply, reply_markup=main_menu())

    send_voice(reply, message.chat.id, bot)

# ===== RUN =====
print("Bot running...")
bot.infinity_polling()