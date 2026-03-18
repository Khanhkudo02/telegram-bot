from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=False  # luôn hiển thị menu
    )

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