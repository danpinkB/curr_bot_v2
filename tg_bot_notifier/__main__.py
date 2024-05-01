import asyncio
import logging
import os
import time
from typing import Final, Optional

from telegram import Bot

from abstract.const import EXCHANGES
from inmemory_storage.sync_db.sync_db import sync_db
from inmemory_storage.tg_settings_db.structures import TelegramSettings
from inmemory_storage.tg_settings_db.tg_settings_db import tg_settings_db
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
    for chat_id in os.listdir(f'{os.getcwd()}/.var/users'):
        await bot.send_message(chat_id, to_message(message))


class SettingReqCacher:
    def __init__(self):
        self._settings: Optional[TelegramSettings] = None
        self._last_requested_time = 0
        self._setting_db: Final = tg_settings_db()

    async def get_settings(self) -> TelegramSettings:
        now = time.time()
        if not self._settings or now - self._last_requested_time > 2:
            self._last_requested_time = now
            self._settings = await self._setting_db.get_settings()
            return self._settings

        return self._settings


async def main():
    broker = await message_broker()
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    settings_cacher = SettingReqCacher()
    locker_db: Final = sync_db()
    message: ExchangeInstrumentDifference
    settings: TelegramSettings
    m_key: str
    async for message in subscribe_notification_topic(broker):
        # print(message)
        settings = await settings_cacher.get_settings()
        m_key = message.instrument.name
        if (message.buy_price-message.sell_price)/message.buy_price >= settings.percent and not await locker_db.is_lock(m_key):
            await publish_telegram_notification(message, bot)
            await locker_db.lock_action(m_key, settings.messages_delay*1000)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

