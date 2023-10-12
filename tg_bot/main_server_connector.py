import os
import rpyc


class MainServerRpycConnector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        while True:
            try:
                self._conn = rpyc.connect(os.environ.get("MAIN_SERVER_HOST"), os.environ.get("MAIN_SERVER_PORT"))
                return
            except ConnectionRefusedError:
                continue

    def get_ex_unactive_pairs(self, ex: str):
        return self._conn.root.get_ex_unactive_pairs(ex) or "nothing"

    def activate_exchange_pair(self, ex: str, symbol: str) -> str:
        return self._conn.root.activate_exchange_pair(ex, symbol)

    def deactivate_exchange_pair(self, ex: str, symbol: str) -> str:
        return self._conn.root.deactivate_exchange_pair(ex, symbol)

    def deactivate_pair(self, symbol: str) -> str:
        return self._conn.root.deactivate_pair(symbol)

    def activate_pair(self, symbol: str) -> str:
        return self._conn.root.activate_exchange_pair(symbol)

    def get_exchanges(self):
        return self._conn.root.get_exchanges()

    def start(self) -> str:
        return self._conn.root.start_parsing()

    def stop(self) -> str:
        return self._conn.root.stop_parsing()

    def get_price(self, symbol) -> str:
        return self._conn.root.get_price(symbol) or "pair isnt active"
