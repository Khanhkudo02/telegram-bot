import telebot
from openai import OpenAI

BOT_TOKEN = "8668169502:AAE0uPh0sFh051RcEJj-CQv-TMvj6XNlcdE"
OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Xin chào! Tôi là bot AI 🤖 Hãy hỏi tôi bất cứ điều gì.")

@bot.message_handler(func=lambda message: True)
def chat(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": message.text}
            ]
        )

        reply = response.choices[0].message.content
        bot.reply_to(message, reply)

    except Exception as e:
        bot.reply_to(message, "Bot đang gặp lỗi, thử lại sau.")

bot.infinity_polling()