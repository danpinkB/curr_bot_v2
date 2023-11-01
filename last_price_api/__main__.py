import asyncio
import json
import logging
import time
from _decimal import Decimal
from typing import Dict, Optional

from kv_db.db_tg_settings.db_tg_settings import db_tg_settings
from kv_db.db_tg_settings.structures import TelegramSettings

from aiohttp import web

from abstract.const import INSTRUMENTS
from abstract.exchange import Exchange
from abstract.instrument import Instrument
from last_price_api.env import LAST_PRICE_API__PORT
from message_broker.async_rmq_connection import RMQConnectionAsync
from message_broker.message_broker import message_broker
from message_broker.topics.notification import ExchangeInstrumentDifference, publish_notification_topic
from message_broker.topics.price import LastPriceMessage, InstrumentPrice, subscribe_price_topic
JSON_HEADERS = {'Content-Type': 'application/json'}

INSTRUMENT_PRICES: Dict[Instrument, Dict[Exchange, Optional[InstrumentPrice]]] = dict()
for i in INSTRUMENTS.keys():
    INSTRUMENT_PRICES[i.instrument] = dict()
    INSTRUMENT_PRICES[i.instrument][i.exchange] = None


async def _consume_callback(ex_last_price: LastPriceMessage, broker: RMQConnectionAsync, required_percent: Decimal):
    INSTRUMENT_PRICES[ex_last_price.instrument][ex_last_price.exchange] = ex_last_price.price
    # TODO send price to historical
    for exchange, price in INSTRUMENT_PRICES[ex_last_price.instrument].items():
        if ex_last_price.exchange == exchange or price is None:
            continue
        await send_difference(broker, ex_last_price.instrument, ex_last_price.exchange, ex_last_price.price, exchange, price, required_percent)
        await send_difference(broker, ex_last_price.instrument, exchange, price, ex_last_price.exchange, ex_last_price.price, required_percent)


async def send_difference(broker: RMQConnectionAsync, instrument: Instrument, current_exchange: Exchange, current_price: InstrumentPrice, exchange: Exchange, price: InstrumentPrice, required_percent: Decimal) -> None:
    price_difference = ExchangeInstrumentDifference(
        instrument=instrument,
        buy_exchange=current_exchange,
        buy_price=current_price.buy,
        sell_exchange=exchange,
        sell_price=price.sell,
    )
    if current_price.buy < price.sell and price_difference.calc_difference() > required_percent:
        logging.info(instrument.name, price_difference.calc_difference())
        await publish_notification_topic(broker, price_difference)


async def handle_get_price(request: web.Request) -> web.Response[Dict[str, InstrumentPrice]]:
    instrument = int(request.query["instrument"])
    res = {k.name: {"buy": str(v.buy), "sell": str(v.sell)} for k, v in INSTRUMENT_PRICES.get(Instrument(instrument), {}).items()}
    return web.Response(body=json.dumps(res), headers=JSON_HEADERS)


async def handle_hi(request: web.Request) -> web.Response[str]:
    return web.Response(body="HI")


async def main():
    app = web.Application()
    telegram_settings_rconn = db_tg_settings()
    app.add_routes([
        web.get("/", handle_hi),
        web.get('/price', handle_get_price),
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", LAST_PRICE_API__PORT)
    await site.start()
    broker = await message_broker()
    # TODO fill from historical .var
    message: LastPriceMessage
    lp_time = time.time()
    settings: TelegramSettings = await telegram_settings_rconn.get_settings()
    async for message in subscribe_price_topic(broker):
        now = time.time()
        if now - lp_time > 10:
            lp_time = time.time()
            settings = await telegram_settings_rconn.get_settings()
        if message.exchange == Exchange.UNISWAP:
            logging.info(message)
        await _consume_callback(message, broker, settings.percent)


if __name__ == "__main__":
    from abstract.logger_wrapper import wrap_logger
    wrap_logger()
    asyncio.run(main())
