import json
import logging
import os
from typing import Any, Optional, Dict
from urllib.request import Request

import httpx
from httpx import Response
from httpx._types import RequestData
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from abstract.exchange import Exchange
from abstract.instrument import Instrument
from inmemory_storage.sync_db.sync_db import sync_db
from inmemory_storage.tg_settings_db.structures import TelegramSettings
from tg_bot_management.env import DB_PATH, MANAGEMENT_API_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_PASSWORD


def check_user(err):
    def decorator(func):
        def wrapper(service, update: Update, context: ContextTypes.DEFAULT_TYPE):
            if os.path.exists(f"{DB_PATH}/.var/users/{update.message.chat_id}"):
                return func(service, update, context)
            return err(service, update, context)

        return wrapper
    return decorator


help_registry = list()


def tg_handler_name(name: str, description: str):
    help_registry.append(description)
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.handler_name = name
        wrapper.handler_description = description
        return wrapper
    return decorator


async def request_management_api(method: str, postfix: str, data: Any = None, headers: Dict[str, str] = {}) -> Response:
    async with httpx.AsyncClient() as client:
        print(MANAGEMENT_API_URL)
        return await client.request(method, MANAGEMENT_API_URL+postfix, json=data, headers=headers)


class TGBotMainService:

    def __init__(self) -> None:
        self._tg_bot_server = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        self._help_command = list()
        self._locker_db = sync_db()
        self._tg_bot_server.add_handler(CommandHandler("price", self.get_price))
        self._tg_bot_server.add_handler(CommandHandler("help", self.get_help))
        self._tg_bot_server.add_handler(CommandHandler("ssettings", self.set_settings))
        self._tg_bot_server.add_handler(CommandHandler("settings", self.get_settings))
        self._tg_bot_server.add_handler(CommandHandler("password", self.authorize))
        self._tg_bot_server.add_handler(CommandHandler("ignore", self.ignore))
        self._tg_bot_server.add_handler(CommandHandler("track", self.track))
        # for management_action in getattr(TGBotMainService, '__abstractmethods__'):
        #     method = self.__getattribute__(management_action)
        #     self._help_command.append(method.handler_description)
            # if method.handler_name not in actions:
            #
            #     self._tg_bot_server.add_handler(CommandHandler(method.handler_name, method))
            #     actions.add(method.handler_name)

    async def send_not_allowed_exception(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("you are not allowed")

    def run_polling(self, *args, **kwargs) -> None:
        self._tg_bot_server.run_polling(*args, **kwargs)

    async def authorize(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command, password = update.message.text.split(" ")
        if password == TELEGRAM_BOT_PASSWORD:
            with open(f"{DB_PATH}/.var/users/{update.message.chat_id}", "w+"):
                await update.message.reply_text("your welcome")

    @tg_handler_name("price", "/price [symbol] - get symbol prices")
    @check_user(send_not_allowed_exception)
    async def get_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        symbol_ = update.message.text.split(" ")[1].strip()
        instrument = Instrument.from_str(f'{symbol_}__USDT')
        if not instrument:
            await update.message.reply_text("invalid instrument symbol")
            return
        prices = json.loads((await request_management_api("GET", f"/price/{instrument}")).json())
        res = f"{instrument.name} price: \n"
        print(prices)
        for e, p in prices.items():
            if p:
                res += f' {Exchange(int(e)).name}: \n   buy {round(p.get("buy"), 4)} \n   sell {round(p.get("sell"), 4)}\n'
        await update.message.reply_text(
            res
        )

    @tg_handler_name("settings", "/settings - get settings")
    @check_user(send_not_allowed_exception)
    async def get_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            (await request_management_api("GET", f"/telegram/settings")).json()
        )

    @tg_handler_name("ignore", "/ignore [symbol]")
    @check_user(send_not_allowed_exception)
    async def ignore(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        symbol_ = update.message.text.split(" ")[1].strip()
        if symbol_:
            instrument = Instrument.from_str(f'{symbol_}__USDT')
            if not instrument:
                await update.message.reply_text("invalid instrument symbol")
                return
            self._locker_db.infinite_lock(instrument.name)
            await update.message.reply_text(f"{instrument.name} is ignoring")

    @tg_handler_name("track", "/track [symbol]")
    @check_user(send_not_allowed_exception)
    async def track(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        symbol_ = update.message.text.split(" ")[1].strip()
        if symbol_:
            instrument = Instrument.from_str(f'{symbol_}__USDT')
            if not instrument:
                await update.message.reply_text("invalid instrument symbol")
                return
            self._locker_db.infinite_realize(instrument.name)
            await update.message.reply_text(f"{instrument.name} is checking")

    @check_user(send_not_allowed_exception)
    async def get_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("\n".join(help_registry))

    @tg_handler_name("ssettings", "/ssettings [percent] [calc_volume] [messages_delay]")
    @check_user(send_not_allowed_exception)
    async def set_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        settings: TelegramSettings = (await request_management_api("GET", f"/telegram/settings")).json()
        args = update.message.text.split(" ")
        old_settings = [(k, v) for k, v in settings.items()]
        new_settings = {}
        key: str
        for ind_, arg in enumerate(args[1:]):
            key = old_settings[ind_][0]
            new_settings[key] = arg if arg != "-" else old_settings[ind_][1]

        await update.message.reply_text((await request_management_api("PUT", f"/telegram/settings", new_settings, headers={"Content-Type": "application/json"})).json())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tg_bot_server = TGBotMainService()
    tg_bot_server.run_polling()
