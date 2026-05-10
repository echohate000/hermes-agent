import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

SYSTEM_PROMPT = "Ты опытный программист-помощник. Помогаешь писать, объяснять и исправлять код. Когда пишешь код — всегда оборачивай его в ```язык ... ```. Объясняй понятно. Отвечай на том языке на котором пишет пользователь."

histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💻 Привет! Я твой ИИ-помощник по коду.\n\n"
        "Я умею:\n"
        "• Писать код на любом языке\n"
        "• Объяснять как работает код\n"
        "• Находить и исправлять ошибки\n\n"
        "Просто напиши что нужно сделать!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    await update.message.chat.send_action("typing")

    if user_id not in histories:
        histories[user_id] = []

    histories[user_id].append({"role": "user", "parts": [{"text": text}]})

    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}",
            json={
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "contents": histories[user_id]
            }
        )
        data = response.json()
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        histories[user_id].append({"role": "model", "parts": [{"text": answer}]})

        if len(answer) > 4096:
            for i in range(0, len(answer), 4096):
                await update.message.reply_text(answer[i:i+4096])
        else:
            await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    histories[user_id] = []
    await update.message.reply_text("🔄 Память очищена!")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(Command
