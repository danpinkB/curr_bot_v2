import ast
import json
from typing import NamedTuple, Tuple

from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address


class PairRow(NamedTuple):
    symbol: str
    token0: ChecksumAddress
    token1: ChecksumAddress
    chain: int

    @staticmethod
    def from_row(row: Tuple[str, str, str, int]) -> 'PairRow':
        return PairRow(
            symbol=row[0],
            token0=to_checksum_address(row[1]),
            token1=to_checksum_address(row[2]),
            chain=row[3]
        )

    @staticmethod
    def from_string(data: str) -> "PairRow":
        return PairRow.from_row(ast.literal_eval(data))

    def to_string(self) -> str:
        return str(self.to_row())

    def to_row(self) -> Tuple[str, str, str, int]:
        return self.symbol, str(self.token0), str(self.token1), self.chain

