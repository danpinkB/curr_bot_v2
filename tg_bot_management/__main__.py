import logging
import os
from typing import Optional

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from web3._utils.module_testing.go_ethereum_personal_module import PASSWORD

from obs_shared.types.management_web_service import MainServiceBase
from tg_bot_management.env import DB_PATH, TELEGRAM_BOT_TOKEN
from tg_bot_management.main_server_connector import MainServerRpycConnector


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


class TGBotMainService(MainServiceBase):
    def __init__(self) -> None:
        self._tg_bot_server = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        self._help_command = list()
        actions = set()
        for management_action in getattr(MainServiceBase, '__abstractmethods__'):
            method = self.__getattribute__(management_action)
            if method.handler_name not in actions:
                self._help_command.append(method.handler_description)
                self._tg_bot_server.add_handler(CommandHandler(method.handler_name, method))
                actions.add(method.handler_name)

        self._tg_bot_server.add_handler(CommandHandler("help", self.get_help))
        self._tg_bot_server.add_handler(CommandHandler("password", self.authorize))
        self._main_connector = MainServerRpycConnector()

    async def send_not_allowed_exception(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("you are not allowed")

    def run_polling(self, *args, **kwargs) -> None:
        self._tg_bot_server.run_polling(*args, **kwargs)

    async def _activate_pair_hole(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        split_command_args = update.message.text.split(" ")
        if len(split_command_args) == 2:
            await update.message.reply_text(self._main_connector.activate_pair(split_command_args[1]))
        if len(split_command_args) == 3:
            await update.message.reply_text(
                self._main_connector.activate_exchange_pair(split_command_args[1], split_command_args[2]))

    async def _deactivate_pair_hole(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        split_command_args = update.message.text.split(" ")
        if len(split_command_args) == 2:
            await update.message.reply_text(self._main_connector.deactivate_pair(split_command_args[1]))
        if len(split_command_args) == 3:
            await update.message.reply_text(self._main_connector.deactivate_exchange_pair(split_command_args[1], split_command_args[2]))

    async def _price_hole(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        split_command_args = update.message.text.split(" ")
        logging.info(f"command args {split_command_args}")
        if len(split_command_args) == 2:
            command, symbol = update.message.text.split(" ")
            await update.message.reply_text(self._main_connector.get_price(symbol+"USDT"))
        if len(split_command_args) == 3:
            command, ex_name, symbol = update.message.text.split(" ")
            await update.message.reply_text(self._main_connector.activate_exchange_pair(ex_name, symbol+"USDT"))

    @tg_handler_name("deactivate", "/deactivate [ex_name] [symbol] - ban ex pair")
    @check_user(send_not_allowed_exception)
    async def deactivate_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        return await self._deactivate_pair_hole(update, context)

    async def authorize(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command, password = update.message.text.split(" ")
        if password == PASSWORD:
            with open(f"{DB_PATH}/data/users/{update.message.chat_id}", "w"):
                await update.message.reply_text("your welcome")

    @tg_handler_name("activate", "/activate [ex_name] [symbol] - unban ex pair")
    @check_user(send_not_allowed_exception)
    async def activate_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        return await self._activate_pair_hole(update, context)

    @tg_handler_name("deactivate", "/deactivate [ex_name] [symbol] - ban ex pair")
    @check_user(send_not_allowed_exception)
    async def deactivate_exchange_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        return await self._deactivate_pair_hole(update, context)

    @tg_handler_name("activate", "/activate [ex_name] [symbol] - unban ex pair")
    @check_user(send_not_allowed_exception)
    async def activate_exchange_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command, ex_name, symbol = update.message.text.split(" ")
        await update.message.reply_text(self._main_connector.activate_exchange_pair(ex_name, symbol))

    @tg_handler_name("exdpairs", "/exdpairs [ex_name] - get ex banned pairs")
    @check_user(send_not_allowed_exception)
    async def get_ex_banned_pairs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command, ex_name = update.message.text.split(" ")
        await update.message.reply_text(self._main_connector.get_ex_banned_pairs(ex_name))

    @tg_handler_name("price", "/price [symbol] - get symbol prices")
    @check_user(send_not_allowed_exception)
    async def get_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        return await self._price_hole(update, context)

    @tg_handler_name("price", "/price [symbol] - get symbol prices")
    @check_user(send_not_allowed_exception)
    async def get_exchange_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        return await self._price_hole(update, context)

    @tg_handler_name("exchanges", "/exchanges - get exchanges names")
    @check_user(send_not_allowed_exception)
    async def get_exchanges(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        names = self._main_connector.get_exchanges()
        logging.info(f"names:{names}")
        await update.message.reply_text(names)

    @check_user(send_not_allowed_exception)
    async def get_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("\n".join(self._help_command))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tg_bot_server = TGBotMainService()
    tg_bot_server.run_polling()
