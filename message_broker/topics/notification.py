import contextlib
from _decimal import Decimal
from typing import NamedTuple, AsyncIterator

from aio_pika.abc import AbstractIncomingMessage

from abstract.exchange import Exchange
from abstract.instrument import Instrument
from message_broker.async_rmq_connection import RMQConnectionAsync

TOPIC__NOTIFICATION = "notification"


# class ExchangeInstrumentDifferenceMessageWrapper:
#     def __init__(self, iterator: AsyncIterator[AbstractIncomingMessage]) -> None:
#         self._iterator = iterator
#
#     async def __anext__(self) -> 'ExchangeInstrumentDifference':
#         message: AbstractIncomingMessage = await anext(self._iterator)
#         async with message.process():
#             return ExchangeInstrumentDifference.from_bytes(message.body)


async def subscribe_notification_topic(conn: RMQConnectionAsync) -> AsyncIterator['ExchangeInstrumentDifference']:
    async with conn.persistent_subscribe(TOPIC__NOTIFICATION, TOPIC__NOTIFICATION) as iterator:
        async for message in iterator:
            async with message.process():
                yield ExchangeInstrumentDifference.from_bytes(message.body)
        # yield ExchangeInstrumentDifferenceMessageWrapper(iterator)


async def publish_notification_topic(conn: RMQConnectionAsync, data: 'ExchangeInstrumentDifference') -> None:
    await conn.persistent_publish(TOPIC__NOTIFICATION, TOPIC__NOTIFICATION, data.to_bytes())


class ExchangeInstrumentDifference(NamedTuple):
    instrument: Instrument
    buy_exchange: Exchange
    buy_price: Decimal
    sell_exchange: Exchange
    sell_price: Decimal

    def calc_difference(self) -> Decimal:
        return ((self.sell_price - self.buy_price) / self.buy_price) * 100

    def to_bytes(self) -> bytes:
        from_price = str(self.buy_price).encode("ascii")
        to_price = str(self.sell_price).encode("ascii")
        return bytes([
            *self.buy_exchange.value.to_bytes(2, "little"),
            *self.sell_exchange.value.to_bytes(2, "little"),
            *self.instrument.value.to_bytes(2, "little"),
            len(from_price),
            *from_price,
            len(to_price),
            *to_price
        ])

    @staticmethod
    def from_bytes(data: bytes) -> 'ExchangeInstrumentDifference':
        ind = 7
        from_p_len = data[ind-1]
        from_price = data[ind:ind + from_p_len].decode("ascii")
        ind += from_p_len + 1
        to_p_len = data[ind-1]
        to_price = data[ind:ind+to_p_len].decode("ascii")
        return ExchangeInstrumentDifference(
            buy_exchange=Exchange(data[0]),
            buy_price=Decimal(from_price),
            sell_exchange=Exchange(data[2]),
            sell_price=Decimal(to_price),
            instrument=Instrument(data[4]),
        )
