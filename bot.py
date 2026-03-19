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
bot = telebot.TeleBot(BOT_TOKEN)

# ===== STATE =====
# Lưu trạng thái của từng user: "search" | "weather" | None
user_state = {}


# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    user_state.pop(message.chat.id, None)
    bot.send_message(
        message.chat.id,
        "🤖 *AI BOT PRO*\n\nChọn chức năng bên dưới 👇",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


# ===== FILE =====
@bot.message_handler(content_types=['document'])
def file_handler(message):
    handle_file(bot, message)


# ===== OCR IMAGE =====
@bot.message_handler(content_types=['photo'])
def image_handler(message):
    handle_image(bot, message)


# ===== VOICE INPUT =====
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded = bot.download_file(file_info.file_path)

        with open("voice.ogg", "wb") as f:
            f.write(downloaded)

        text = voice_to_text("voice.ogg")
        if not text or "❌" in text:
            bot.send_message(message.chat.id, "❌ Không nhận diện được giọng nói.")
            return

        bot.send_message(message.chat.id, f"📝 Bạn nói: *{text}*", parse_mode="Markdown")

        reply = ask_ai(text, message.chat.id)
        bot.send_message(message.chat.id, reply, reply_markup=main_menu())

        # Chỉ gửi voice nếu reply ngắn (tránh lag)
        if len(reply) <= 300:
            send_voice(reply, message.chat.id, bot)

    except Exception as e:
        print(f"[VOICE ERROR] {e}")
        bot.send_message(message.chat.id, "❌ Lỗi xử lý giọng nói.")


# ===== CHAT =====
@bot.message_handler(func=lambda message: True)
def chat(message):
    text = message.text
    if not text:
        return

    chat_id = message.chat.id
    state = user_state.get(chat_id)

    # ===== XỬ LÝ STATE =====

    # State: đang chờ nhập thành phố
    if state == "weather":
        user_state.pop(chat_id, None)
        city = text.strip()
        bot.send_message(chat_id, get_weather(city), reply_markup=main_menu())
        return

    # State: đang chờ nhập từ khóa tìm kiếm
    if state == "search":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "🔍 Đang tìm kiếm...")
        result = search_web(text)
        bot.send_message(chat_id, result, reply_markup=main_menu())
        return

    # ===== MENU BUTTONS =====

    if text == "🌤 Thời tiết":
        user_state[chat_id] = "weather"
        bot.send_message(chat_id, "🏙 Nhập tên thành phố (VD: Hanoi, Ho Chi Minh):")
        return

    if text == "🌐 Tìm kiếm":
        user_state[chat_id] = "search"
        bot.send_message(chat_id, "🔎 Nhập nội dung cần tìm:")
        return

    if text == "🤖 Chat AI":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "💬 Hãy hỏi tôi bất cứ điều gì!", reply_markup=main_menu())
        return

    if text == "📄 Đọc file":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "📎 Gửi file PDF, DOCX hoặc Excel cho tôi.", reply_markup=main_menu())
        return

    if text == "🎤 Voice":
        user_state.pop(chat_id, None)
        bot.send_message(chat_id, "🎤 Hãy gửi tin nhắn thoại cho tôi.", reply_markup=main_menu())
        return

    # ===== KEYWORD SHORTCUTS =====
    text_lower = text.lower()

    if any(x in text_lower for x in ["thời tiết", "nhiệt độ", "trời hôm nay"]):
        user_state[chat_id] = "weather"
        bot.send_message(chat_id, "🏙 Nhập tên thành phố:")
        return

    if any(x in text_lower for x in ["tìm kiếm", "tin tức", "bitcoin", "usd", "giá vàng", "giá dầu"]):
        user_state[chat_id] = "search"
        bot.send_message(chat_id, "🔎 Nhập nội dung cần tìm:")
        return

    # ===== AI =====
    try:
        bot.send_chat_action(chat_id, "typing")
        reply = ask_ai(text, chat_id)
        bot.send_message(chat_id, reply, reply_markup=main_menu())

        # Chỉ gửi voice nếu reply ngắn (tránh lag)
        if len(reply) <= 300:
            send_voice(reply, chat_id, bot)

    except Exception as e:
        print(f"[AI ERROR] {e}")
        bot.send_message(chat_id, "❌ Lỗi AI, thử lại sau.", reply_markup=main_menu())


# ===== RUN =====
print("✅ Bot running...")
bot.infinity_polling()