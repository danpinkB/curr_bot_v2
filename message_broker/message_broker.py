from message_broker.async_rmq_connection import RMQConnectionAsync
from message_broker.env import MESSAGE_BROKER__DSN


async def message_broker() -> RMQConnectionAsync:
    return await RMQConnectionAsync.connect(MESSAGE_BROKER__DSN)
