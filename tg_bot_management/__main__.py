import logging
import os
from typing import Any, Optional
from urllib.request import Request

import httpx
from httpx import Response
from httpx._types import RequestData
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from web3._utils.module_testing.go_ethereum_personal_module import PASSWORD

from tg_bot_management.env import DB_PATH, MANAGEMENT_API_URL, TELEGRAM_BOT_TOKEN


def check_user(err):
    def decorator(func):
        def wrapper(service, update: Update, context: ContextTypes.DEFAULT_TYPE):
            print(os.getcwd())

            if os.path.exists(f"{os.getcwd()}/data/users/{update.message.chat_id}"):
                return func(service, update, context)
            return err(service, update, context)

        return wrapper
    return decorator


def tg_handler_name(name: str, description: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.handler_name = name
        wrapper.handler_description = description
        return wrapper
    return decorator


async def request_management_api(method: Request, data: Optional[RequestData] = None) -> Response:
    async with httpx.AsyncClient() as client:
        return await client.request(MANAGEMENT_API_URL, method.method, data=data)


class TGBotMainService:

    def __init__(self) -> None:
        self._tg_bot_server = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        self._help_command = list()
        self._tg_bot_server.add_handler(CommandHandler("price", self.get_price))
        self._tg_bot_server.add_handler(CommandHandler("exchanges", self.get_exchanges))
        self._tg_bot_server.add_handler(CommandHandler("setting", self.set_setting))
        self._tg_bot_server.add_handler(CommandHandler("ssettings", self.set_settings))
        self._tg_bot_server.add_handler(CommandHandler("password", self.authorize))

    async def send_not_allowed_exception(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("you are not allowed")

    def run_polling(self, *args, **kwargs) -> None:
        self._tg_bot_server.run_polling(*args, **kwargs)

    async def authorize(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command, password = update.message.text.split(" ")
        if password == PASSWORD:
            with open(f"{DB_PATH}/data/users/{update.message.chat_id}", "w"):
                await update.message.reply_text("your welcome")

    @tg_handler_name("price", "/price [symbol] - get symbol prices")
    @check_user(send_not_allowed_exception)
    async def get_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        split_command_args = update.message.text.split(" ")
        logging.info(f"command args {split_command_args}")
        if len(split_command_args) == 2:
            command, symbol = update.message.text.split(" ")
            await update.message.reply_text(self._main_connector.get_price(symbol))
        if len(split_command_args) == 3:
            command, ex_name, symbol = update.message.text.split(" ")
            await update.message.reply_text(self._main_connector.activate_exchange_pair(ex_name, symbol))


    @tg_handler_name("exchanges", "/exchanges - get exchanges names")
    @check_user(send_not_allowed_exception)
    async def get_exchanges(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(names)

    @check_user(send_not_allowed_exception)
    async def get_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("\n".join(self._help_command))

    @tg_handler_name("setting", "/setting [setting_name] [setting_value]")
    @check_user(send_not_allowed_exception)
    async def set_setting(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command, setting_name, setting_value = update.message.text.split(" ")
        await update.message.reply_text(self._main_connector.set_setting(setting_name, setting_value))

    @tg_handler_name("ssettings", "/ssettings [percent] [delay_mills] [rvolume] [mdelay]")
    @check_user(send_not_allowed_exception)
    async def set_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        settings = self._main_connector.get_settings()
        args = update.message.text.split(" ")
        new_settings = list()
        old_settings = settings.to_row()
        for ind_, arg in enumerate(args[1:]):
            new_settings[ind_] = arg if arg != "-" else old_settings[ind_]

        await update.message.reply_text(self._main_connector.set_settings(ComparerSettings.from_row(tuple[str, str, str, str](new_settings))))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tg_bot_server = TGBotMainService()
    tg_bot_server.run_polling()
