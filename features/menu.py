from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("🤖 Chat AI","🌤 Thời tiết")
    m.row("🌐 Tìm kiếm","📄 Đọc file")
    m.row("🎤 Voice")
    return m