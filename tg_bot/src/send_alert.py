import asyncio
import os

from telegram import Bot

bot = Bot(token=os.environ.get("TELEGRAM_BOT_API_TOKEN"))
DB_PATH = os.environ.get("DB_PATH")


async def send_alert(message: str) -> None:
    for chat_id in os.listdir(f'{DB_PATH}/data/users'):
        await bot.send_message(chat_id, message)

