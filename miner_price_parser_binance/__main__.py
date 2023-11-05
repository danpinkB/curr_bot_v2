import asyncio
import time
from _decimal import Decimal
from datetime import datetime
from typing import Dict, Union

from aio_binance.futures.usdt import WsClient

from abstract.logger_wrapper import wrap_logger
from abstract.exchange import Exchange
from abstract.instrument import Instrument
from message_broker.async_rmq_connection import RMQConnectionAsync
from message_broker.message_broker import message_broker
from message_broker.topics.price import publish_price_topic, InstrumentPrice, LastPriceMessage
from miner_price_parser_binance.binance_book_ticker_msg import BinanceBookTickerMsg
from miner_price_parser_binance.const import REQUIRED_INSTRUMENTS, SYMBOL_INSTRUMENT

logger = wrap_logger(__file__)


FIXED_COMMISSION = Decimal('0.1')


class BinanceSocketListener:
    def __init__(self, broker: RMQConnectionAsync, show_stats_every: int) -> None:
        self._broker = broker

        self._started_at = datetime.now()

        self._stats_instrument_count: Dict[Instrument, int] = {instrument: 0 for instrument in REQUIRED_INSTRUMENTS}
        self._stats_book_ticker_event_count = 0
        self._stats_show_every = show_stats_every
        self._stats_prev_time = 0.

    def _collect_and_show_book_ticker_stats(self, instrument: Instrument) -> None:
        if self._stats_show_every <= 0:
            return
        if not self._stats_prev_time:
            self._stats_prev_time = time.time()
            self._start_dt = datetime.now()
        self._stats_instrument_count[instrument] += 1
        self._stats_book_ticker_event_count += 1
        if self._stats_book_ticker_event_count % self._stats_show_every == 0:
            now = time.time()
            logger.info(
                f'book_ticker {self._stats_show_every / (now - self._stats_prev_time):,.3f} msg/s '
                f'({self._stats_book_ticker_event_count} events from {self._started_at.isoformat()})'
            )
            self._stats_prev_time = now

    async def handle_stream_router(self, msg: Dict[str, Union[Dict[str, Union[int, str]], str]]) -> None:
        stream: str = msg.get('stream')
        if stream.endswith('@bookTicker'):
            data = BinanceBookTickerMsg(msg)
            if data.has_error:
                logger.warning(f"invalid binance response. skipped.", extra={'biance_message': msg})
                return
            self._collect_and_show_book_ticker_stats(data.instrument)
            return await self.handle_book_ticker(data)
        logger.error(f'not implemented handler for "{stream}" stream name')

    async def handle_book_ticker(self, data: BinanceBookTickerMsg) -> None:
        await publish_price_topic(self._broker, LastPriceMessage(
            price=InstrumentPrice(
                buy=data.best_bid_price,
                sell=data.best_ask_price,
                buy_fee=FIXED_COMMISSION,
                sell_fee=FIXED_COMMISSION,
                # TODO: timestamp
                # TODO: quantities
            ),
            exchange=Exchange.BINANCE,
            instrument=data.instrument,
        ))


async def main() -> None:
    broker = await message_broker()
    listener = BinanceSocketListener(broker, show_stats_every=10_000)
    ws = WsClient()
    streams = [ws.stream_book_ticker(symbol) for symbol in SYMBOL_INSTRUMENT.keys()]
    res = await asyncio.gather(*streams)
    await ws.subscription_streams(res, listener.handle_stream_router)


if __name__ == "__main__":
    asyncio.run(main())
