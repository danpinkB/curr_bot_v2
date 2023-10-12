import logging
import os

from obs_shared.types.management_web_service import MainServiceBase
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from const import TELEGRAM_BOT_API_TOKEN
from main_server_connector import MainServerRpycConnector

from dotenv import load_dotenv

load_dotenv()

app = ApplicationBuilder().token(TELEGRAM_BOT_API_TOKEN).build()


class TGBotMainService(MainServiceBase):
    def __init__(self) -> None:
        self._main_connector = MainServerRpycConnector()

    async def deactivate_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        splitted_data = update.message.text.split(" ")
        if len(splitted_data) == 2:
            command, symbol = update.message.text.split(" ")
            await update.message.reply_text(self._main_connector.deactivate_pair(symbol))
        if len(splitted_data) == 3:
            command, ex_name, symbol = update.message.text.split(" ")
            await update.message.reply_text(self._main_connector.deactivate_exchange_pair(ex_name, symbol))
        return self._main_connector.deactivate_pair()

    async def activate_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        pass

    async def deactivate_exchange_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        pass

    async def activate_exchange_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        pass

    async def get_ex_banned_pairs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        command, ex_name = update.message.text.split(" ")
        await update.message.reply_text(self._main_connector.get_ex_unactive_pairs(ex_name))

    async def get_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        pass

    async def get_exchanges(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        names = self._main_connector.get_exchanges()
        logging.info(f"names:{names}")
        await update.message.reply_text(names)


def check_user(user_id: int) -> bool:
    return os.path.exists(f"{DB_PATH}/data/users/{user_id}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user(update.message.chat_id):
        await update.message.reply_text("you are not allowed")
    else:
        await update.message.reply_text(main_server_connector.start())


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user(update.message.chat_id):
        await update.message.reply_text("you are not allowed")
    else:
        await update.message.reply_text(main_server_connector.stop())



async def get_ex_unactive_pairs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user(update.message.chat_id):
        await update.message.reply_text("you are not allowed")
    else:
        command, ex_name = update.message.text.split(" ")
        await update.message.reply_text(main_server_connector.get_ex_unactive_pairs(ex_name))


async def deactivate_pair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user(update.message.chat_id):
        await update.message.reply_text("you are not allowed")
        return
    else:
        splitted_data = update.message.text.split(" ")
        if len(splitted_data) == 2:
            command, symbol = update.message.text.split(" ")
            await update.message.reply_text(main_server_connector.deactivate_pair(symbol))
        if len(splitted_data) == 3:
            command, ex_name, symbol = update.message.text.split(" ")
            await update.message.reply_text(main_server_connector.deactivate_exchange_pair(ex_name, symbol))


async def activate_pair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user(update.message.chat_id):
        await update.message.reply_text("you are not allowed")
        return
    else:
        splitted_data = update.message.text.split(" ")
        if len(splitted_data) == 2:
            command, symbol = splitted_data
            await update.message.reply_text(main_server_connector.activate_pair(symbol))
        if len(splitted_data) == 3:
            command, ex_name, symbol = splitted_data
            await update.message.reply_text(main_server_connector.activate_exchange_pair(ex_name, symbol))


async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command, password = update.message.text.split(" ")
    if password == PASSWORD:
        with open(f"{DB_PATH}/data/users/{update.message.chat_id}", "w"):
            await update.message.reply_text("your welcome")


help = """
/exchanges - get exchanges names\n
/exdpairs [ex_name] - get ex banned pairs\n
/price [symbol] - get symbol prices\n
/deactivate [ex_name] [symbol] - ban ex pair\n
/deactivate [symbol] - get ex banned pairs\n
/activate [ex_name] [symbol] - unban ex pair\n
/activate [symbol] - unban pair\n
/price [COIN_PAIR] - get pair prices\n
  """


async def send_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user(update.message.from_user.id):
        await update.message.reply_text("you are not allowed")
    else:
        await update.message.reply_text(help)


async def pair_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user(update.message.from_user.id):
        await update.message.reply_text("you are not allowed")
    else:
        command, symbol = update.message.text.split(" ")
        await update.message.reply_text(main_server_connector.get_price(symbol))


app.add_handler(CommandHandler("help", send_help))
app.add_handler(CommandHandler("password", password))
app.add_handler(CommandHandler("start_parsing", start))
app.add_handler(CommandHandler("stop_parsing", stop))
app.add_handler(CommandHandler("price", pair_price))
app.add_handler(CommandHandler("exchanges", get_exchanges))
app.add_handler(CommandHandler("exdpairs", get_ex_unactive_pairs))
app.add_handler(CommandHandler("deactivate", deactivate_pair))
app.add_handler(CommandHandler("activate", activate_pair))
logging.basicConfig(level=logging.INFO)
app.run_polling()
