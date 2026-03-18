from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("🤖 Chat AI"),
        KeyboardButton("🌤 Thời tiết")
    )

    markup.row(
        KeyboardButton("🌐 Tìm kiếm"),
        KeyboardButton("📄 Đọc file")
    )

    markup.row(
        KeyboardButton("🎤 Voice")
    )

    return markup