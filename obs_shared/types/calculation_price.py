import ast
from typing import NamedTuple, Optional, Tuple

from .price_row import PriceRow


class CalculationPrice(NamedTuple):
    group: int
    symbol: str
    exchange: str
    price: PriceRow
    buy: bool

    @staticmethod
    def from_row(data: Tuple[str, str, str, str, Optional[str]]) -> "CalculationPrice":
        return CalculationPrice(
            group=int(data[0]),
            symbol=data[1],
            exchange=data[2],
            price=PriceRow.from_row(data[3]),
            buy=bool(int(data[4])) if data[4] is not None else None
        )

    @staticmethod
    def from_bytes(data: bytes) -> "CalculationPrice":
        return CalculationPrice.from_row(ast.literal_eval(data.decode("utf-8")))

    def to_bytes(self) -> bytes:
        return bytes(str(self.to_row()), "utf-8")

    def to_row(self) -> Tuple[str, str, str, str, Optional[str]]:
        return str(self.group), self.symbol, self.exchange, self.price.to_row(), None if self.buy is None else str(int(self.buy))
