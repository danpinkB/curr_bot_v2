from _decimal import Decimal
from typing import NamedTuple

from eth_typing import ChecksumAddress


class DEXToken(NamedTuple):
    symbol: str
    address: ChecksumAddress
    decimals: Decimal


class CEXToken(NamedTuple):
    symbol: str
