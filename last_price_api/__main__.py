import logging
import time
from _decimal import Decimal
from datetime import datetime, timezone

from pika import spec
from pika.adapters.blocking_connection import BlockingChannel

from last_price_api.env import REDIS_DSN__PRICE, REDIS_DSN__SETTINGS, \
    RABBITMQ_QUE__SENDER, RABBITMQ_QUE__CONSUMER, RMQ_HOST, RMQ_USER, RMQ_PASSWORD
from obs_shared.connection.active_settings_management_rconn import ActiveSettingsManagementRConnection
from obs_shared.connection.price_db_rconn import PriceRConnection
from obs_shared.connection.rabbit_mq_connection import RMQConnection
from obs_shared.types.calculation_difference import CalculationDifference
from obs_shared.types.calculation_price import CalculationPrice
from obs_shared.types.comparer_settings import ComparerSettings

icons = ['⚪️', '🔶']

setting_rconn = ActiveSettingsManagementRConnection(REDIS_DSN__SETTINGS)
consumer = RMQConnection(RMQ_HOST, RMQ_USER, RMQ_PASSWORD)
sender = RMQConnection(RMQ_HOST, RMQ_USER, RMQ_PASSWORD)
price_rconn = PriceRConnection(REDIS_DSN__PRICE)

ZERO = Decimal(0)
groups = [dict(), dict()]

settings = setting_rconn.get_setting()
settings_last_parsed_time = time.time()


def _get_settings() -> ComparerSettings:
    global settings
    if time.time() - settings_last_parsed_time > 60:
        settings = setting_rconn.get_setting()
    return settings


def _consume_callback(ch: BlockingChannel, method: spec.Basic.Deliver, properties: spec.BasicProperties, body: bytes):
    calc_price = CalculationPrice.from_bytes(body)
    group = groups[calc_price.group]
    logging.info(f"calc_price message {calc_price}")
    if group.get(calc_price.symbol) is None:
        groups[calc_price.group][calc_price.symbol] = dict()

    if calc_price.group == 0:
        groups[calc_price.group][calc_price.symbol][calc_price.exchange] = calc_price.price.price
        _compare_dex_with_cexes(calc_price)
    else:
        groups[calc_price.group][calc_price.symbol][calc_price.exchange] = calc_price.price.price
        _compare_cex_with_dexes(calc_price)


def _compare_dex_with_cexes(calc_price: CalculationPrice):
    symbol = calc_price.symbol
    data = groups[1].get(symbol)
    if data is not None:
        now = datetime.now(timezone.utc).timestamp()
        ex0price: Decimal = calc_price.price[calc_price.buy]
        ex0 = calc_price.exchange
        if calc_price.buy == 1:
            for cex_name, cex_price in data.items():
                if cex_price[0] != ZERO and ex0price < cex_price[0]:
                    diff = cex_price[0] - ex0price
                    perc_diff = (diff / cex_price[0]) * 100
                    send_message_wrapper(icons[0], symbol, perc_diff, ex0, cex_name, ex0price, cex_price[0], now)
        else:
            for cex_name, cex_price in data.items():
                if cex_price[0] != ZERO and ex0price > cex_price[0]:
                    diff = ex0price - cex_price[0]
                    perc_diff = (diff / ex0price) * 100
                    send_message_wrapper(icons[1], symbol, perc_diff, cex_name, ex0, cex_price[0], ex0price, now)


def _compare_cex_with_dexes(calc_price: CalculationPrice) -> None:
    data = groups[0].get(calc_price.symbol)
    if data is not None:
        ex0price: Decimal = calc_price.price[0]
        ex0 = calc_price.exchange
        symbol = calc_price.symbol
        now = datetime.now(timezone.utc).timestamp()
        for dex_ex, dex_buy_sell_prices in data.items():
            if dex_buy_sell_prices[0] != ZERO and dex_buy_sell_prices[0] > ex0price:
                ex1price = dex_buy_sell_prices[0]
                diff = ex1price - ex0price
                perc_diff = (diff / ex1price) * 100
                send_message_wrapper(icons[1], symbol, perc_diff, ex0, dex_ex, ex0price, ex1price, now)
            if dex_buy_sell_prices[1] != ZERO and dex_buy_sell_prices[1] < ex0price:
                ex1price = dex_buy_sell_prices[1]
                diff = ex0price - ex1price
                perc_diff = (diff / ex0price) * 100
                send_message_wrapper(icons[0], symbol, perc_diff, dex_ex, ex0, ex1price, ex0price, now)


def send_message_wrapper(icon: str, symbol: str, perc_diff: Decimal, from_ex: str, to_ex: str, from_price: Decimal, to_price: Decimal, now: float) -> None:
    settings_ = _get_settings()
    if perc_diff > settings_.percent:
        diff_model = CalculationDifference(
            ex_from=from_ex,
            ex_to=to_ex,
            price_from=from_price,
            price_to=to_price,
            diff_percent=perc_diff,
            icon=icon,
            symbol=symbol
        )
        sender.send_message(RABBITMQ_QUE__SENDER, diff_model.to_bytes())
        logging.info(f"{icon} {symbol}, {from_ex}, {to_ex}, {from_price}, {to_price}, {perc_diff}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer.consume(RABBITMQ_QUE__CONSUMER, _consume_callback)

