import logging

import rpyc

from management_api.env import REDIS_DSN__PRICE, REDIS_DSN__SETTINGS, MANAGEMENT_API_PORT
from obs_shared.connection.active_settings_management_rconn import ActiveSettingsManagementRConnection
from obs_shared.connection.price_db_rconn import PriceRConnection
from obs_shared.types.management_web_service import MainServiceBase
from rpyc import ThreadedServer


class MainService(rpyc.Service, MainServiceBase):

    def __init__(self) -> None:
        self._active_settings_rconn = ActiveSettingsManagementRConnection(REDIS_DSN__SETTINGS)
        self._price_rconn = PriceRConnection(REDIS_DSN__PRICE)
        super(MainService, self).__init__()

    def is_alive(self) -> bool:
        return True

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
            res += f"{exchange} : {price.to_printable_str()} \n"
        return res

    def get_exchange_price(self, exchange: str, symbol: str) -> str:
        price = self._price_rconn.get_exchange_pair_price(exchange, symbol)
        return f"{exchange} : {price.to_printable_str()} \n"

    def get_exchanges(self) -> str:
        return ", ".join(self._active_settings_rconn.get_exchanges())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = ThreadedServer(
        service=MainService,
        port=MANAGEMENT_API_PORT,
        protocol_config={"allow_public_attrs": True}
    )
    server.start()