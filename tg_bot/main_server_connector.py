import os
import rpyc
from obs_shared.connection.management_web_service import MainServiceBase

from const import MANAGEMENT_API_URI, MANAGEMENT_API_PORT


class MainServerRpycConnector(MainServiceBase):

    def __init__(self):
        self._service: MainServiceBase = rpyc.connect(MANAGEMENT_API_URI, MANAGEMENT_API_PORT).root

    def deactivate_pair(self, symbol: str) -> str:
        return self._service.deactivate_pair(symbol)

    def activate_pair(self, symbol: str) -> str:
        return self._service.activate_pair(symbol)

    def deactivate_exchange_pair(self, exchange: str, symbol: str) -> str:
        return self._service.deactivate_exchange_pair(exchange, symbol)

    def activate_exchange_pair(self, exchange: str, symbol: str) -> str:
        return self._service.activate_exchange_pair(exchange, symbol)

    def get_ex_banned_pairs(self, exchange: str) -> str:
        return self._service.get_ex_banned_pairs(exchange)

    def get_price(self, symbol) -> str:
        return self._service.get_price(symbol)

    def get_exchanges(self) -> str:
        return self._service.get_exchanges()



    
