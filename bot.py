import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(
    model_name="gemma-3-27b-it",
    system_instruction="""Ты опытный программист-помощник. 
Помогаешь писать, объяснять и исправлять код.
Когда пишешь код — всегда оборачивай его в ```язык ... ```.
Объясняй понятно, как будто объясняешь новичку.
Отвечай на том языке на котором пишет пользователь."""
)

chats = {}

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

    if user_id not in chats:
        chats[user_id] = model.start_chat(history=[])

    try:
        response = chats[user_id].send_message(text)
        answer = response.text

        if len(answer) > 4096:
            for i in range(0, len(answer), 4096):
                await update.message.reply_text(answer[i:i+4096], parse_mode="Markdown")
        else:
            await update.message.reply_text(answer, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in chats:
        del chats[user_id]
    await update.message.reply_text("🔄 Память очищена! Начинаем заново.")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
