import asyncio
import logging
from typing import Dict, Optional

from aiohttp import web
import simplejson as json
from abstract.const import INSTRUMENTS, EXCHANGES
from abstract.exchange import Exchange
from abstract.instrument import Instrument
from last_price_api.env import LAST_PRICE_API_PORT
from message_broker.async_rmq_connection import RMQConnectionAsync
from message_broker.message_broker import message_broker
from message_broker.topics.notification import ExchangeInstrumentDifference, publish_notification_topic
from message_broker.topics.price import LastPriceMessage, InstrumentPrice, subscribe_price_topic

INSTRUMENT_PRICES: Dict[Instrument, Dict[Exchange, Optional[InstrumentPrice]]] = dict()
for i in Instrument:
    INSTRUMENT_PRICES[i] = dict()
    for e in EXCHANGES:
        INSTRUMENT_PRICES[i][e] = None


async def _consume_callback(ex_last_price: LastPriceMessage, broker: RMQConnectionAsync):
    INSTRUMENT_PRICES[ex_last_price.instrument][ex_last_price.exchange] = ex_last_price.price
    #TODO send price to historical
    for exchange, price in INSTRUMENT_PRICES[ex_last_price.instrument].items():
        if ex_last_price.exchange == exchange or price is None:
            continue
        await send_difference(broker, ex_last_price.instrument, ex_last_price.exchange, ex_last_price.price, exchange, price)
        await send_difference(broker, ex_last_price.instrument, exchange, price, ex_last_price.exchange, ex_last_price.price)


async def send_difference(broker: RMQConnectionAsync, instrument: Instrument, current_exchange: Exchange, current_price: InstrumentPrice, exchange: Exchange, price: InstrumentPrice) -> None:
    # logging.info(f'{instrument.name} {current_exchange.name} buy {current_price.buy} \n {exchange.name} sell {price.sell}')
    logging.debug(f'{instrument} {current_price.buy}, {price.sell}')
    if current_price.buy < price.sell:
        await publish_notification_topic(broker, ExchangeInstrumentDifference(
            instrument=instrument,
            buy_exchange=current_exchange,
            buy_price=current_price.buy,
            sell_exchange=exchange,
            sell_price=price.sell,
        ))


async def handle_get_price(request: web.Request) -> web.Response[Dict[str, InstrumentPrice]]:
    instrument = int(request.rel_url.query["instrument"])
    return web.json_response(json.dumps(INSTRUMENT_PRICES.get(Instrument(instrument), {})))


async def main():
    broker = await message_broker()
    # TODO fill from historical .var

    app = web.Application()
    app.add_routes([
        web.get('/price', handle_get_price),
    ])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", LAST_PRICE_API_PORT)

    await site.start()
    print(f"Server started at 0.0.0.0:{LAST_PRICE_API_PORT}")
    message: LastPriceMessage
    async for message in subscribe_price_topic(broker):
        await _consume_callback(message, broker)

    await asyncio.Future()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
