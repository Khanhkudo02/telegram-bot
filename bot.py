import telebot

TOKEN = "8668169502:AAEL5CWwL29nFRRx6gXJGfZ86YcYs7BALsw"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def reply(message):
    bot.reply_to(message, "Xin chào Khánh 👋")

bot.polling()
