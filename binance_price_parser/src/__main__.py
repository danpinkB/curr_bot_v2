import json
from _decimal import Decimal
from typing import Optional

from jinja2 import Template
from obs_shared.connection import RMQConnection, ActiveSettingsRConnection
from obs_shared.types import CalculationPrice

from src.binance import BinanceExchange
from src.const import SENDER_RMQ_QUE, \
    SENDER_RMQ_PASSWORD, SENDER_RMQ_USER, SENDER_RMQ_HOST, SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD, \
    BINANCE_API

setting_rconn: ActiveSettingsRConnection = ActiveSettingsRConnection(SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD)
price_sender: RMQConnection = RMQConnection(SENDER_RMQ_HOST, SENDER_RMQ_USER, SENDER_RMQ_PASSWORD)

ex = BinanceExchange(BINANCE_API)

_key = Template("{{pair}}_price_{{type}}")


if __name__ == '__main__':
    ex.parse_prices({"ETHUSDT"})