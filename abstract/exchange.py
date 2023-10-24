from enum import unique, Enum, IntEnum
from typing import NamedTuple


@unique
class ExchangeKind(Enum):
    DEX = 'DEX'
    CEX = 'CEX'


@unique
class Exchange(IntEnum):
    BINANCE = 1
    UNISWAP = 2

    @property
    def kind(self) -> ExchangeKind:
        from abstract.const import EXCHANGES
        return EXCHANGES[self].kind


class ExchangeParams(NamedTuple):
    name: str
    kind: ExchangeKind
    icon: str
