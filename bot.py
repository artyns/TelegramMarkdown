import telebot
from telebot import types
import json
from flask import Flask
import threading
import time
import requests
import os
app = Flask(__name__)

# آدرس خود سرور
URL = "http://127.0.0.1:5000/"



@app.route("/")
def home():
    return "Server is alive!"

def self_ping():
    while True:
        time.sleep(300)  # 5 دقیقه

        try:
            response = requests.get(URL, timeout=10)
            print(f"[PING] Status: {response.status_code}")
        except Exception as e:
            print(f"[PING] Failed: {e}")

token = os.getenv("TOKEN")

bot = telebot.TeleBot(token)

WEB_APP = "https://artyns.github.io/TelegramMarkdown/?v=6"


@bot.message_handler(commands=["start"])
def start(message):

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    button = types.KeyboardButton(
        "open editor",
        web_app=types.WebAppInfo(
            WEB_APP
        )
    )

    keyboard.add(button)

    bot.send_message(
        message.chat.id,
        "open editor with keyboard",
        reply_markup=keyboard
    )


@bot.message_handler(content_types=["web_app_data"])
def get_webapp(message):

    data = json.loads(
        message.web_app_data.data
    )

    text = data.get("text", "")


    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    button = types.KeyboardButton(
        "open editor",
        web_app=types.WebAppInfo(
            WEB_APP
        ),
        style=""
    )

    keyboard.add(button)

    bot.send_message(
        message.chat.id,
        "open editor with keyboard",
        reply_markup=keyboard
    )


    if not text:
        bot.send_message(
            message.chat.id,
            "   ‌ ‌. "
        )
        return


    rich = types.InputRichMessage(
        markdown=text
    )


    bot.send_rich_message(
        chat_id=message.chat.id,
        rich_message=rich
    )



@bot.inline_handler(func=lambda q: True)
def inline(q):
    
    user_input = q.query

    rich = types.InputRichMessage(
        markdown=user_input
    )

    result = types.InlineQueryResultArticle(
        id=1,
        title="rich message",
        input_message_content=types.InputRichMessageContent(
            rich_message=rich
        ))
        
    error = types.InlineQueryResultArticle(
    id=1,
    title="error ، ریدی داش",
    input_message_content=types.InputTextMessageContent(
        message_text="Error"
    )
)
        
    try:
        bot.answer_inline_query(
        q.id,
        [result],
        cache_time=0
    )
    
    except:
        bot.answer_inline_query(
        q.id,
        [error],
        cache_time=0
    )
        
        
def runFlask():
        port = int(os.environ.get("PORT", 5000))
        app.run(
        host=port,
        port=5000
    )
        
if __name__ == "__main__":
    threading.Thread(target=self_ping, daemon=True).start()
    threading.Thread(target=runFlask, daemon=True).start()

    

bot.infinity_polling()
