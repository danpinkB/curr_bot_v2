import ast
import json
from _decimal import Decimal
from typing import NamedTuple, Tuple


class CalculationDifference(NamedTuple):
    icon: str
    symbol: str
    ex_from: str
    ex_to: str
    price_from: Decimal
    price_to: Decimal
    diff_percent: Decimal

    @staticmethod
    def from_row(data: Tuple[str, str, str, str, str, str, str]) -> "CalculationDifference":
        return CalculationDifference(
            icon=data[0],
            symbol=data[1],
            ex_from=data[2],
            ex_to=data[3],
            price_from=Decimal(data[4]),
            price_to=Decimal(data[5]),
            diff_percent=Decimal(data[6])
        )

    @staticmethod
    def from_bytes(data: bytes) -> "CalculationDifference":
        return CalculationDifference.from_row(ast.literal_eval(data.decode("utf-8")))

    def to_bytes(self) -> bytes:
        return bytes(str(self.to_row()), "utf-8")

    def to_printable_str(self) -> str:
        return f"{self.icon} {self.ex_from} -> {self.ex_to} \n"\
               f"{round(self.price_from, 8)} -> {round(self.price_to, 8)} \n"\
               f"{round(self.diff_percent, 0)}"

    def to_row(self) -> Tuple[str, str, str, str, str, str, str]:
        return self.icon, self.symbol, self.ex_from, self.ex_to, str(self.price_from), str(self.price_to), str(
            self.diff_percent)
