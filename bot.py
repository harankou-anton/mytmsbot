# bot.py
import os
import random

import aioredis


from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler
import logging

from telegram.ext.filters import TEXT

redis = aioredis.from_url("redis://localhost")
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
logger = logging.getLogger(__name__)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await redis.lpush("chats_correct", update.effective_chat.id)
    logger.info(
        f'Chat ID: {update.effective_chat.id}'
        f'User: {update.effective_user.first_name}'
    )
    await update.message.reply_text(
        f"Hello {update.effective_user.first_name}"
    )

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(
        f'Chat ID: {update.effective_chat.id}'
        f'User: {update.effective_user.first_name}'
    )
    await update.message.reply_text(
        f"{update.message.text}"
    )


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters=TEXT, callback=message))
    app.run_polling()

