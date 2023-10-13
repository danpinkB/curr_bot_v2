import logging
import os
import time
from _decimal import Decimal
from datetime import datetime, timezone

from obs_shared.connection import RMQConnection, ActiveSettingsExchangeRConnection, PriceRConnection
from obs_shared.types import CalculationPrice, ComparerSettings, CalculationDifference
from pika import spec
from pika.adapters.blocking_connection import BlockingChannel

from src.env import SENDER_RMQ_HOST, SENDER_RMQ_USER, SENDER_RMQ_PASSWORD, CONSUMER_RMQ_PASSWORD, CONSUMER_RMQ_USER, \
    CONSUMER_RMQ_HOST, CONSUMER_RMQ_QUE, SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD, SENDER_RMQ_QUE, \
    PRICE_R_HOST, PRICE_R_DB, PRICE_R_PASSWORD

icons = ['⚪️', '🔶']

setting_rconn = ActiveSettingsExchangeRConnection(SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD)
consumer = RMQConnection(CONSUMER_RMQ_HOST, CONSUMER_RMQ_USER, CONSUMER_RMQ_PASSWORD)
sender = RMQConnection(SENDER_RMQ_HOST, SENDER_RMQ_USER, SENDER_RMQ_PASSWORD)
price_rconn = PriceRConnection(PRICE_R_HOST, PRICE_R_DB, PRICE_R_PASSWORD)

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
    if group.get(calc_price.symbol) is None:
        group[calc_price.symbol] = dict()
    if group[calc_price.symbol].get(calc_price.exchange) is None:
        group[calc_price.symbol][calc_price.exchange] = list(range(2 if calc_price.group == 0 else 1))

    if calc_price.group == 0:
        group[calc_price.symbol][calc_price.exchange][calc_price.buy] = calc_price.price
        _compare_dex_with_cexes(calc_price.symbol, calc_price.exchange, calc_price.price, calc_price.buy)
    else:
        group[calc_price.symbol][calc_price.exchange][0] = calc_price.price
        _compare_cex_with_dexes(calc_price.symbol, calc_price.exchange, calc_price.price)


def _compare_dex_with_cexes(symbol: str, ex0: str, ex0price: Decimal, buy: int):
    data = groups[1].get(symbol)
    if len(data) > 0:
        now = datetime.now(timezone.utc).timestamp()
        if buy == 1:
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


def _compare_cex_with_dexes(symbol: str, ex0: str, ex0price: Decimal) -> None:
    data = groups[0].get(symbol)
    if len(data) > 0:
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
        # key = f"{symbol}{from_ex}{to_ex}"
        # if messages.get(key) is not None:
        #     if now - messages[key] < TELEGRAM_BOT_ALERT_DELAY:
        #         return
        # messages[key] = now
        bytes(symbol, 'utf-8')
        sender.send_message(SENDER_RMQ_QUE, diff_model.to_bytes())
        # send_alert(f'{icon} {symbol.replace("USDT","")}:{from_ex}->{to_ex} {round(perc_diff, 2)}%\n {round(from_price, 8)}->{round(to_price, 8)}')
        logging.info(f"{icon} {symbol}, {from_ex}, {to_ex}, {from_price}, {to_price}, {perc_diff}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # server = ThreadedServer(ComparerService, port=os.environ.get("CALCULATION_SERVER_PORT"), protocol_config={"allow_public_attrs": True}, listener_timeout=None)
    logging.info(f"PORT {os.environ.get('CALCULATION_SERVER_PORT')}")
    consumer.consume(CONSUMER_RMQ_QUE, _consume_callback)

