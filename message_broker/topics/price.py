from _decimal import Decimal
from typing import NamedTuple, AsyncIterator

from aio_pika.abc import AbstractIncomingMessage

from abstract.exchange import Exchange
from abstract.instrument import Instrument
from message_broker.async_rmq_connection import RMQConnectionAsync

TOPIC__PRICE = "price"


async def subscribe_price_topic(conn: RMQConnectionAsync) -> AsyncIterator['LastPriceMessage']:
    message: AbstractIncomingMessage
    async with conn.persistent_subscribe(TOPIC__PRICE, TOPIC__PRICE) as iterator:
        async for message in iterator:
            async with message.process():
                yield LastPriceMessage.from_bytes(message.body)


async def publish_price_topic(conn: RMQConnectionAsync, data: 'LastPriceMessage') -> None:
    await conn.persistent_publish(TOPIC__PRICE, TOPIC__PRICE, data.to_bytes())


class InstrumentPrice(NamedTuple):
    buy: Decimal
    sell: Decimal
    buy_fee: Decimal
    sell_fee: Decimal


class LastPriceMessage(NamedTuple):
    exchange: Exchange
    instrument: Instrument
    price: InstrumentPrice

    def to_bytes(self) -> bytes:
        buy = str(self.price.buy).encode("ascii")
        sell = str(self.price.sell).encode("ascii")
        buy_fee = str(self.price.buy_fee).encode("ascii")
        sell_fee = str(self.price.sell_fee).encode("ascii")
        return bytes([
            self.exchange.value,
            *self.instrument.value.to_bytes(2, "little"),
            len(buy),
            *buy,
            len(sell),
            *sell,
            len(buy_fee),
            *buy_fee,
            len(sell_fee),
            *sell_fee
        ])

    @staticmethod
    def from_bytes(data: bytes) -> 'LastPriceMessage':
        ind = 4
        buy_len = data[ind - 1]
        buy_s = data[ind: ind + buy_len].decode("ascii")
        ind += buy_len + 1
        sell_len = data[ind - 1]
        sell_s = data[ind: ind + sell_len].decode("ascii")
        ind += sell_len + 1
        buy_fee_len = data[ind - 1]
        buy_fee_s = data[ind: ind + buy_fee_len].decode("ascii")
        ind += buy_fee_len + 1
        sell_fee_len = data[ind - 1]
        sell_fee_s = data[ind: ind + sell_fee_len].decode("ascii")
        return LastPriceMessage(
            exchange=Exchange(data[0]),
            instrument=Instrument(int.from_bytes(data[1:2], "little")),
            price=InstrumentPrice(
                buy=Decimal(buy_s),
                sell=Decimal(sell_s),
                buy_fee=Decimal(buy_fee_s),
                sell_fee=Decimal(sell_fee_s)
            ),
        )



