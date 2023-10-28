import logging
import os
from typing import Optional

import httpx
from httpx import Response
from httpx._types import RequestData
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.ext._utils.types import HandlerCallback, CCT, RT
from web3._utils.module_testing.go_ethereum_personal_module import PASSWORD

from abstract.instrument import Instrument
from kv_db.db_tg_settings.structures import TelegramSettings
from tg_bot_management.const import HELP_MESSAGE
from tg_bot_management.env import DB_PATH, MANAGEMENT_API_URL, TELEGRAM_BOT_TOKEN


async def send_not_allowed_exception(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("you are not allowed")


def check_user(update: Update) -> bool:
    return os.path.exists(f"{os.getcwd()}/.var/users/{update.message.chat_id}")


def check_user_decorator() -> HandlerCallback[Update, CCT, RT]:
    def decorator(func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> HandlerCallback[Update, CCT, RT] | None:
            if check_user(update):
                return await func(update, context)
            return await send_not_allowed_exception(update, context)

        return wrapper
    return decorator


async def authorize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command, password = update.message.text.split(" ")
    if password == PASSWORD:
        with open(f"{DB_PATH}/data/users/{update.message.chat_id}", "w"):
            await update.message.reply_text("your welcome")


async def request_management_api(postfix: str, method: str, data: Optional[RequestData] = None) -> Response:
    async with httpx.AsyncClient() as client:
        return await client.request(f'{MANAGEMENT_API_URL}{postfix}', method, data=data)

@check_user_decorator
async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    split_command_args = update.message.text.split(" ")
    command, symbol = update.message.text.split(" ")
    price = await request_management_api(f"/price", "get", Instrument(f'{symbol}__USDT'))
    await update.message.reply_text()

@check_user_decorator
async def get_exchanges(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    resp = await request_management_api("/exchanges", "get", None)
    await update.message.reply_text(resp.text)

@check_user_decorator
async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_MESSAGE)


@check_user_decorator
async def set_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command, setting_name, setting_value = update.message.text.split(" ")
    resp = await request_management_api("/exchanges", "put", None)
    await update.message.reply_text(self._main_connector.set_setting(setting_name, setting_value))

@check_user_decorator
async def set_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    settings = self._main_connector.get_settings()
    args = update.message.text.split(" ")
    new_settings = list()
    old_settings = settings.to_row()
    for ind_, arg in enumerate(args[1:]):
        new_settings[ind_] = arg if arg != "-" else old_settings[ind_]

    await update.message.reply_text(self._main_connector.set_settings(TelegramSettings(*new_settings)))

def main():
    tg_bot_server = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    tg_bot_server.add_handler(CommandHandler("price", get_price))
    tg_bot_server.add_handler(CommandHandler("exchanges", get_exchanges))
    tg_bot_server.add_handler(CommandHandler("setting", set_setting))
    tg_bot_server.add_handler(CommandHandler("ssettings", set_settings))
    tg_bot_server.add_handler(CommandHandler("password",    authorize))




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tg_bot_server = TGBotMainService()
    tg_bot_server.run_polling()
