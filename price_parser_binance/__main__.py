import asyncio
import functools
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
SYMBOL_INSTRUMENT = {INSTRUMENTS[ExchangeInstrument(Exchange.BINANCE, i)].cex.base.symbol+INSTRUMENTS[ExchangeInstrument(Exchange.BINANCE, i)].cex.quote.symbol: i for i in REQUIRED_INSTRUMENTS}
from dotenv import load_dotenv
load_dotenv()


async def handle_socket_message(msg: Dict, *, broker: RMQConnectionAsync):
    data = msg.get("data")
    if data is None:
        traceback.print_stack()
        logging.info(f"{msg}")
        return
    await publish_price_topic(
        broker,
        LastPriceMessage(
            price=InstrumentPrice(
                buy=Decimal(data['b']),
                sell=Decimal(data['a']),
                buy_fee=Decimal('0.1'),
                sell_fee=Decimal('0.1')
            ),
            exchange=Exchange.BINANCE,
            instrument=SYMBOL_INSTRUMENT[data['s']]
        )
    )


async def main():
    ws = WsClient()
    ws.stream_book_ticker().close()
    broker = await message_broker()
    streams = [ws.stream_book_ticker(instrument_symbol) for instrument_symbol in REQUIRED_INSTRUMENTS]
    res = await asyncio.gather(*streams)
    await ws.subscription_streams(res, functools.partial(handle_socket_message, broker=broker))


if __name__ == "__main__":
    asyncio.run(main())



