import asyncio
import logging
import os

from telegram import Bot

from abstract.const import EXCHANGES
from message_broker.message_broker import message_broker
from message_broker.topics.notification import ExchangeInstrumentDifference, subscribe_notification_topic
from tg_bot_notifier.env import TELEGRAM_BOT_TOKEN


def to_message(message: ExchangeInstrumentDifference):
    buy_ex = EXCHANGES[message.buy_exchange]
    sell_ex = EXCHANGES[message.sell_exchange]
    return (
        f'{buy_ex.icon} {message.instrument.name.replace("__USDT", "")}: {buy_ex.name} -> {sell_ex.name} {round(message.calc_difference(), 2)} % \n'
        f'{round(message.buy_price, 8)} -> {round(message.sell_price, 8)}')


async def publish_telegram_notification(message: ExchangeInstrumentDifference, bot) -> None:
    for chat_id in os.listdir(f'{os.getcwd()}/data/users'):
        await bot.send_message(chat_id, to_message(message))


async def main():
    broker = await message_broker()
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    message: ExchangeInstrumentDifference
    async for message in subscribe_notification_topic(broker):
        await publish_telegram_notification(message, bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

