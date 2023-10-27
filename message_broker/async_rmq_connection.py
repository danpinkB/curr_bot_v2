import contextlib
from typing import Type, TypeVar

import aio_pika
from aio_pika.abc import AbstractRobustConnection, ExchangeType, DeliveryMode, AbstractQueueIterator

T = TypeVar('T', bound='RMQConnectionAsync')


class RMQConnectionAsync:
    def __init__(self, connection: AbstractRobustConnection) -> None:
        self._connection: AbstractRobustConnection = connection

    @classmethod
    async def connect(cls: Type[T], dsn: str) -> T:
        connection = await aio_pika.connect_robust(dsn)
        return RMQConnectionAsync(connection)

    @contextlib.asynccontextmanager
    async def persistent_subscribe(self, exchange_name: str, queue_name: str) -> AbstractQueueIterator:
        async with self._connection.channel() as channel:
            await channel.set_qos(prefetch_count=1)
            exchange = await channel.declare_exchange(exchange_name, ExchangeType.TOPIC)
            queue = await channel.declare_queue(queue_name, durable=True)
            await queue.bind(exchange, routing_key=queue_name)
            yield queue.iterator()

    async def persistent_publish(self, exchange_name: str, queue_name: str, message: bytes) -> None:
        # Sending a message
        async with self._connection.channel() as channel:
            await channel.declare_queue(queue_name, durable=True)
            exchange = await channel.declare_exchange(exchange_name, ExchangeType.TOPIC)
            await exchange.publish(
                aio_pika.Message(body=message, delivery_mode=DeliveryMode.PERSISTENT),
                routing_key=queue_name
            )

