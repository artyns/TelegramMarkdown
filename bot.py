import telebot
from telebot import types
import uuid
import traceback

from flask import Flask
import threading
import requests
import os
import time


# =========================
# Telegram Bot
# =========================

Token = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")

bot = telebot.TeleBot(Token)


HelpText = rf"""
# Heading 1
{"\n"}
\# Heading 1

---

## Heading 2
{"\n"}
\#\# Heading 2

---

### Heading 3
{"\n"}
\#\#\# Heading 3

---

#### Heading 4
{"\n"}
\#\#\#\# Heading 4

---

**Bold** text:
{"\n"}
\*\* Bold \*\*

---

_Italic_ text
{"\n"}
\_Italic\_

---

__Underline__ text
{"\n"}
\_\_Underline\_\_

---

||Spoiler|| text
{"\n"}
\|\|Spoiler\|\|

---

***Bold Italic***
{"\n"}
\*\*\*Bold Italic\*\*\*

---

**~~Bold Strike~~**
{"\n"}
\*\*\~\~Bold Strike\~\~\*\*

---

| Header 1 | Header 2 | Header 3 |
|---|---|---|
| Value 1 | Value 2 | Value 3 |

---

- [X] checked
- [ ] Unchecked

---

- first
- second
"""


@bot.message_handler(commands=["start"])
def start(message):
    try:
        rich = types.InputRichMessage(
            markdown=HelpText
        )

        bot.send_rich_message(
            chat_id=message.chat.id,
            rich_message=rich
        )

    except Exception:
        print("START ERROR:")
        traceback.print_exc()


@bot.inline_handler(func=lambda q: True)
def inline(q):
    try:
        user_input = q.query

        rich = types.InputRichMessage(
            markdown=user_input
        )

        result = types.InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title="rich message",
            input_message_content=types.InputRichMessageContent(
                rich_message=rich
            )
        )

        bot.answer_inline_query(
            q.id,
            [result],
            cache_time=0
        )

    except Exception:
        print("INLINE ERROR:")
        traceback.print_exc()

        try:
            error = types.InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="Error",
                input_message_content=types.InputTextMessageContent(
                    message_text="Error while processing Rich Message"
                )
            )

            bot.answer_inline_query(
                q.id,
                [error],
                cache_time=0
            )

        except Exception:
            print("ERROR RESPONSE FAILED:")
            traceback.print_exc()


# =========================
# Flask Server
# =========================

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is alive!"


# =========================
# Self Ping
# =========================

def self_ping():
    while True:
        try:
            time.sleep(300)  # 5 minutes

            url = os.environ.get("RENDER_EXTERNAL_URL")

            if not url:
                print("RENDER_EXTERNAL_URL is not set")
                continue

            response = requests.get(
                url,
                timeout=20
            )

            print(
                f"Self ping: {response.status_code}"
            )

        except Exception:
            print("SELF PING ERROR:")
            traceback.print_exc()


# =========================
# Start Flask
# =========================

def run_flask():
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )


# =========================
# Start Everything
# =========================

if __name__ == "__main__":

    # Flask
    threading.Thread(
        target=run_flask,
        daemon=True
    ).start()

    # Self ping
    threading.Thread(
        target=self_ping,
        daemon=True
    ).start()

    # Telegram polling
    while True:
        try:
            bot.infinity_polling(
                skip_pending=True,
                timeout=30,
                long_polling_timeout=30
            )

        except Exception:
            print("POLLING ERROR:")
            traceback.print_exc()

            time.sleep(5)