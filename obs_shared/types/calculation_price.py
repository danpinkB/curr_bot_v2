import ast
from typing import NamedTuple, Optional, Tuple

from .price_row import PriceRow


class CalculationPrice(NamedTuple):
    group: int
    symbol: str
    exchange: str
    price: PriceRow
    buy: Optional[int]

    @staticmethod
    def from_row(data: Tuple[int, str, str, str, Optional[int]]) -> "CalculationPrice":
        return CalculationPrice(
            group=data[0],
            symbol=data[1],
            exchange=data[2],
            price=PriceRow.from_row(data[3]),
            buy=data[4]
        )

    @staticmethod
    def from_bytes(data: bytes) -> "CalculationPrice":
        return CalculationPrice.from_row(ast.literal_eval(data.decode("utf-8")))

    def to_bytes(self) -> bytes:
        return bytes(str(self.to_row()), "utf-8")

    def to_row(self) -> Tuple[int, str, str, str, Optional[int]]:
        return self.group, self.symbol, self.exchange, self.price.to_row(), self.buy
