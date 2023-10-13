import logging
from typing import Optional, Set

from obs_shared.types.management_web_service import MainServiceBase
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from src.env import TELEGRAM_BOT_TOKEN
from src.main_server_connector import MainServerRpycConnector


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
            print(method)
            if method.handler_name not in actions:
                self._help_command.append(method.handler_description)
                self._tg_bot_server.add_handler(CommandHandler(method.handler_name, method))
                actions.add(method.handler_name)

        self._tg_bot_server.add_handler(CommandHandler("help", self.get_help))
        self._main_connector = MainServerRpycConnector()

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
            await update.message.reply_text(
                self._main_connector.deactivate_exchange_pair(split_command_args[1], split_command_args[2]))

    async def _price_hole(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        split_command_args = update.message.text.split(" ")
        if len(split_command_args) == 2:
            command, symbol = update.message.text.split(" ")
            await update.message.reply_text(self._main_connector.get_price(symbol))
        if len(split_command_args) == 3:
            command, ex_name, symbol = update.message.text.split(" ")
            await update.message.reply_text(self._main_connector.activate_exchange_pair(ex_name, symbol))

    @tg_handler_name("deactivate", "/deactivate [ex_name] [symbol] - ban ex pair")
    async def deactivate_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        return await self._deactivate_pair_hole(update, context)

    @tg_handler_name("activate", "/activate [ex_name] [symbol] - unban ex pair")
    async def activate_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        return await self._activate_pair_hole(update, context)

    @tg_handler_name("deactivate", "/deactivate [ex_name] [symbol] - ban ex pair")
    async def deactivate_exchange_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        return await self._deactivate_pair_hole(update, context)

    @tg_handler_name("activate", "/activate [ex_name] [symbol] - unban ex pair")
    async def activate_exchange_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command, ex_name, symbol = update.message.text.split(" ")
        await update.message.reply_text(self._main_connector.activate_exchange_pair(ex_name, symbol))

    @tg_handler_name("exdpairs", "/exdpairs [ex_name] - get ex banned pairs")
    async def get_ex_banned_pairs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        command, ex_name = update.message.text.split(" ")
        await update.message.reply_text(self._main_connector.get_ex_banned_pairs(ex_name))

    @tg_handler_name("price", "/price [symbol] - get symbol prices")
    async def get_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        return await self._price_hole(update, context)

    @tg_handler_name("price", "/price [symbol] - get symbol prices")
    async def get_exchange_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
        return await self._price_hole(update, context)

    @tg_handler_name("exchanges", "/exchanges - get exchanges names")
    async def get_exchanges(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        names = self._main_connector.get_exchanges()
        logging.info(f"names:{names}")
        await update.message.reply_text(names)

    async def get_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("\n".join(self._help_command))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tg_bot_server = TGBotMainService()
    tg_bot_server.run_polling()
