from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🤖 Chat AI"),
        KeyboardButton("🌤 Thời tiết")
    )
    markup.add(
        KeyboardButton("🌐 Tìm kiếm"),
        KeyboardButton("📄 Đọc file")
    )
    markup.add(KeyboardButton("🎤 Voice"))
    return markup