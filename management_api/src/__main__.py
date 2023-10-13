import logging
from typing import Optional

import rpyc
from obs_shared.connection import PriceRConnection
from obs_shared.connection.active_settings_management_rconn import ActiveSettingsManagementRConnection

from obs_shared.types import PriceRow
from obs_shared.types.management_web_service import MainServiceBase
from rpyc import ThreadedServer

from src.const import SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD, PRICE_R_HOST, PRICE_R_DB, PRICE_R_PASSWORD, \
    MANAGEMENT_API_PORT


class MainService(rpyc.Service, MainServiceBase):

    def __init__(self) -> None:
        self._active_settings_rconn = ActiveSettingsManagementRConnection(SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD)
        self._price_rconn = PriceRConnection(PRICE_R_HOST, PRICE_R_DB, PRICE_R_PASSWORD)
        super(MainService, self).__init__()

    def on_connect(self, conn: rpyc.core.protocol.Connection):
        logging.info("Client connected.")

    def on_disconnect(self, conn):
        logging.info("Client disconnected.")

    def deactivate_pair(self, symbol: str) -> str:
        for exchange in self._active_settings_rconn.get_exchanges():
            self._active_settings_rconn.deactivate_ex_pair(exchange, symbol)
        return f"{symbol} deactivated"

    def activate_pair(self, symbol: str) -> str:
        for exchange in self._active_settings_rconn.get_exchanges():
            self._active_settings_rconn.activate_ex_pair(exchange, symbol)
        return f"{symbol} activated"

    def deactivate_exchange_pair(self, exchange: str, symbol: str) -> str:
        self._active_settings_rconn.deactivate_ex_pair(exchange, symbol)
        return f"{exchange}-{symbol} was deactivated"

    def activate_exchange_pair(self, exchange: str, symbol: str) -> str:
        self._active_settings_rconn.activate_ex_pair(exchange, symbol)
        return f"{exchange}-{symbol} was activated"

    def get_ex_banned_pairs(self, exchange: str) -> str:
        return ", ".join(self._active_settings_rconn.get_exchange_banned_pairs(exchange))

    def get_price(self, symbol) -> str:
        res = ""
        symbol = symbol + "USDT"
        for exchange, price in self._price_rconn.get_pair_exchanges_prices(symbol).items():
            res += f"{exchange} : {PriceRow(price)} \n"
        return res

    def get_exchange_price(self, exchange: str, symbol: str) -> str:
        price = self._price_rconn.get_exchange_pair_price(exchange, symbol)
        return f"{exchange} : {PriceRow(price)} \n"

    def get_exchanges(self) -> str:
        return ", ".join(self._active_settings_rconn.get_exchanges())


if __name__ == "__main__":
    server = ThreadedServer(
        service=MainService,
        port=MANAGEMENT_API_PORT,
        protocol_config={"allow_public_attrs": True}
    )
    server.start()