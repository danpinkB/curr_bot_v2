from _decimal import Decimal
from typing import NamedTuple

from eth_typing import ChecksumAddress


class DEXToken(NamedTuple):
    symbol: str
    address: ChecksumAddress
    decimals: int


class CEXToken(NamedTuple):
    symbol: str
