import asyncio
import logging
import os

from pika import spec
from pika.adapters.blocking_connection import BlockingChannel
from telegram import Bot

from obs_shared.connection.active_settings_management_rconn import ActiveSettingsManagementRConnection
from obs_shared.connection.rabbit_mq_connection import RMQConnection
from obs_shared.connection.sync_db_rconn import SyncRConnection
from obs_shared.types.calculation_difference import CalculationDifference
from tg_bot_notification_handler.env import TELEGRAM_BOT_TOKEN, RABBITMQ_QUE__CONSUMER, \
    REDIS_DSN__SETTINGS, RABBITMQ_DSN__CONSUMER, REDIS_DSN__SYNC

bot = Bot(token=TELEGRAM_BOT_TOKEN)
consumer = RMQConnection(RABBITMQ_DSN__CONSUMER, RABBITMQ_QUE__CONSUMER)

setting_rconn: ActiveSettingsManagementRConnection = ActiveSettingsManagementRConnection(REDIS_DSN__SETTINGS)
sync_rconn: SyncRConnection = SyncRConnection(REDIS_DSN__SYNC)


async def send_alert(message: str) -> None:
    #os.getcwd()
    for chat_id in os.listdir(f'{os.getcwd()}/data/users'):
        await bot.send_message(chat_id, message)


def _consume_callback(ch: BlockingChannel, method: spec.Basic.Deliver, properties: spec.BasicProperties, body: bytes):
    calc_diff = CalculationDifference.from_bytes(body)
    mess_key = f'{calc_diff.symbol}{calc_diff.ex_from}{calc_diff.ex_to}'
    logging.info(f"key {mess_key}")
    if not sync_rconn.is_lock(mess_key):
        sync_rconn.lock_action(mess_key, setting_rconn.get_setting().mdelay*1000)
        asyncio.run(send_alert(calc_diff.to_printable_str()))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer.consume(RABBITMQ_QUE__CONSUMER, _consume_callback)
