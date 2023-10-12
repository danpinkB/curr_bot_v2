import logging
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from main_server_connector import MainServerRpycConnector

from dotenv import load_dotenv
load_dotenv()

app = ApplicationBuilder().token(os.environ.get("TELEGRAM_BOT_API_TOKEN")).build()
main_server_connector = MainServerRpycConnector()
DB_PATH = os.environ.get("DB_PATH")
PASSWORD = os.environ.get("TELEGRAM_BOT_PASSWORD")


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


async def get_exchanges(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not check_user(update.message.chat_id):
        await update.message.reply_text("you are not allowed")
    else:
        names = main_server_connector.get_exchanges()
        logging.info(f"names:{names}")
        await update.message.reply_text(names)


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
