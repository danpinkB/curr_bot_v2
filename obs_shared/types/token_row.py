import ast
import json
from _decimal import Decimal
from typing import NamedTuple, Tuple

from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address


class TokenRow(NamedTuple):
    address: ChecksumAddress
    symbol: str
    full_symbol: str
    decimals: Decimal
    chain: int

    type_ = Tuple[str, str, str, str, int]

    @staticmethod
    def from_row(row: Tuple[str, str, str, str, int]) -> 'TokenRow':
        return TokenRow(
            address=to_checksum_address(row[0]),
            symbol=row[1],
            full_symbol=row[2],
            decimals=Decimal(row[3]),
            chain=row[4]
        )

    @staticmethod
    def from_string(data: str) -> "TokenRow":
        return TokenRow.from_row(ast.literal_eval(data))

    def to_string(self) -> str:
        return str(self.to_row())

    def to_row(self) -> Tuple[str, str, str, str, int]:
        return str(self.address), self.symbol, self.full_symbol, str(self.decimals), self.chain

