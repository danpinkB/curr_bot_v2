from _decimal import Decimal
from typing import Dict, Union

from abstract.instrument import Instrument
from miner_price_parser_binance.const import SYMBOL_INSTRUMENT


class BinanceBookTickerMsg:
    __slots__ = (
        '_response',
    )

    def __init__(self, response: Dict[str, Dict[str, Union[str, int]]]) -> None:
        self._response = response.get('data')

    @property
    def has_error(self) -> bool:
        return self._response is None

    @property
    def best_bid_price(self) -> Decimal:
        return Decimal(self._response['b'])

    @property
    def symbol(self) -> str:
        return self._response['s']

    @property
    def instrument(self) -> Instrument:
        return SYMBOL_INSTRUMENT[self.symbol]

    @property
    def order_book_update_id(self) -> int:
        return self._response['u']

    @property
    def best_bid_quantity(self) -> Decimal:
        return Decimal(self._response['B'])

    @property
    def best_ask_price(self) -> Decimal:
        return Decimal(self._response['a'])

    @property
    def best_ask_quantity(self) -> Decimal:
        return Decimal(self._response['A'])

    @property
    def event_time(self) -> int:
        return self._response['E']

    @property
    def transaction_time(self) -> int:
        return self._response['T']
