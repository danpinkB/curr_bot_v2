import os
from _decimal import Decimal
import rpyc


class CalculationServerRpycConnector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._conn = rpyc.connect(os.environ.get("CALCULATION_SERVER_HOST"), os.environ.get("CALCULATION_SERVER_PORT"))

    def send_add_price(self, symbol: str, ex: str, price: Decimal, group: int) -> None:
        try:
            self._conn.root.add_price(symbol, ex, str(price), group)
        except Exception as ex:
            print(ex)