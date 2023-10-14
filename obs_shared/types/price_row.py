from _decimal import Decimal
from typing import List, NamedTuple


class PriceRow(NamedTuple):
    price: List[Decimal]

    @staticmethod
    def from_row(data: str) -> 'PriceRow':
        return PriceRow(
            price=[Decimal(price_part) for price_part in data.split(',')]
        )

    def to_row(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return ",".join([str(price) for price in self.price])

    def to_printable_str(self) -> str:
        if len(self.price) > 1:
            return f'\n buy {round(self.price[1], 8)}\n sell {round(self.price[0], 8)}'
        else:
            return f' - {round(self.price[0], 8)}'

    def __getitem__(self, index: int) -> Decimal:
        return self.price[index]

    def __setitem__(self, index: int, val: Decimal) -> None:
        self.price[index] = val


