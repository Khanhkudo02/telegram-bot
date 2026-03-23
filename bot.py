import os
import telebot

from features.weather import get_weather
from features.search import search_web
from features.chat_ai import ask_ai
from features.file_reader import handle_file
from features.voice import send_voice
from features.menu import main_menu
from features.ocr import handle_image
from features.speech_to_text import voice_to_text

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ Missing TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

user_state = {}

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    user_state.pop(message.chat.id, None)
    bot.send_message(
        message.chat.id,
        "🤖 AI BOT PRO\n\nChọn chức năng 👇",
        reply_markup=main_menu()
    )

# ===== FILE =====
@bot.message_handler(content_types=['document'])
def file_handler(message):
    handle_file(bot, message)

# ===== IMAGE OCR =====
@bot.message_handler(content_types=['photo'])
def image_handler(message):
    handle_image(bot, message)

# ===== VOICE INPUT =====
@bot.message_handler(content_types=['voice'])
def voice_handler(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        data = bot.download_file(file_info.file_path)

        with open("voice.ogg", "wb") as f:
            f.write(data)

        text = voice_to_text("voice.ogg")
        os.remove("voice.ogg")  # dọn dẹp

        if "lỗi" in text.lower():
            bot.send_message(message.chat.id, text)
            return

        bot.send_message(message.chat.id, f"📝 Đã nhận giọng nói:\n{text}")

        reply = ask_ai(text, message.chat.id)
        bot.send_message(message.chat.id, reply, reply_markup=main_menu())

        if len(reply) < 300:
            send_voice(reply, message.chat.id, bot)

    except Exception as e:
        print(f"VOICE ERROR: {e}")
        bot.send_message(message.chat.id, "❌ Lỗi xử lý voice. Thử lại sau.")

# ===== CHAT / MENU =====
@bot.message_handler(func=lambda m: True)
def chat(message):
    if not message.text:
        return

    text = message.text.strip()
    chat_id = message.chat.id

    # MENU COMMANDS
    if text == "🌤 Thời tiết":
        user_state[chat_id] = "weather"
        bot.send_message(chat_id, "Nhập tên thành phố (ví dụ: Hồ Chí Minh, Hà Nội):")
        return

    if text == "🌐 Tìm kiếm":
        user_state[chat_id] = "search"
        bot.send_message(chat_id, "Nhập nội dung bạn muốn tìm:")
        return

    if text == "📄 Đọc file":
        bot.send_message(chat_id, "Gửi file PDF, Word, Excel cho tôi nhé!")
        return

    if text == "🎤 Voice":
        bot.send_message(chat_id, "Gửi tin nhắn thoại (voice message) cho tôi.")
        return

    # STATE HANDLING
    if user_state.get(chat_id) == "weather":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, get_weather(text), reply_markup=main_menu())
        return

    if user_state.get(chat_id) == "search":
        user_state.pop(chat_id, None)
        result = search_web(text)
        bot.send_message(chat_id, result, reply_markup=main_menu())
        return

    # DEFAULT → AI CHAT
    reply = ask_ai(text, chat_id)
    bot.send_message(chat_id, reply, reply_markup=main_menu())

    if len(reply) < 300:
        send_voice(reply, chat_id, bot)

print("✅ Bot đang chạy...")
bot.infinity_polling()