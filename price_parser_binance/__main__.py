import asyncio
import logging
import traceback
from _decimal import Decimal
from typing import Dict

from aio_binance.futures.usdt import WsClient

from abstract.const import INSTRUMENTS, INSTRUMENTS_CONNECTIVITY
from abstract.exchange import Exchange
from abstract.instrument import ExchangeInstrument
from message_broker.async_rmq_connection import RMQConnectionAsync
from message_broker.message_broker import message_broker
from message_broker.topics.price import publish_price_topic, InstrumentPrice, LastPriceMessage

REQUIRED_INSTRUMENTS = tuple(k for k, v in INSTRUMENTS_CONNECTIVITY.items() if any(ei.exchange == Exchange.BINANCE for ei in v))
SYMBOL_INSTRUMENT = {INSTRUMENTS[ExchangeInstrument(Exchange.BINANCE, i)].cex.base.symbol +
                     INSTRUMENTS[ExchangeInstrument(Exchange.BINANCE, i)].cex.quote.symbol: i for i in REQUIRED_INSTRUMENTS}


class SocketHandler:
    def __init__(self, broker: RMQConnectionAsync) -> None:
        self._broker = broker

    async def handle_socket_message(self, msg: Dict):
        data = msg.get("data")
        if data is None:
            traceback.print_stack()
            logging.info(f"{msg}")
            return
        await publish_price_topic(self._broker, LastPriceMessage(
            price=InstrumentPrice(buy=Decimal(data['b']), sell=Decimal(data['b']), buy_fee=Decimal('0.1'), sell_fee=Decimal('0.1')),
            exchange=Exchange.BINANCE,
            instrument=SYMBOL_INSTRUMENT[data['s']]
        ))


async def callback_event(data: dict):
    print(data)


async def main():
    broker = await message_broker()
    ws = WsClient()
    streams = [ws.stream_book_ticker(symbol) for symbol in SYMBOL_INSTRUMENT.keys()]
    res = await asyncio.gather(*streams)
    await ws.subscription_streams(res, SocketHandler(broker).handle_socket_message)

if __name__ == "__main__":
    from abstract.logger_wrapper import wrap_logger
    wrap_logger()
    asyncio.run(main())
