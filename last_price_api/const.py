from _decimal import Decimal
from enum import Enum, IntEnum
from typing import NamedTuple, Set


class Exchange(IntEnum):
    BINANCE = 1
    UNISWAP = 2


class ExchangeKind(Enum):
    DEX = 'DEX'
    CEX = 'CEX'


class ExchangeParams(NamedTuple):
    kind: ExchangeKind


EXCHANGES = {
    Exchange.BINANCE: ExchangeParams(
        kind=ExchangeKind.CEX,
    ),
    Exchange.UNISWAP: ExchangeParams(
        kind=ExchangeKind.DEX,
    ),
}


class Instrument(IntEnum):
    ETH__USDT = 1
    ARB__USDT = 2
    BTC__USDT = 3

    def exchagnes(self) -> Set[Exchange]:
        return INSTRUMENTS__EXCHANGES[self]


class InstrumentParams(NamedTuple):
    pass


INSTRUMENTS = {
    (Exchange.BINANCE, Instrument.BTC__USDT): InstrumentParams(),
}

INSTRUMENTS__DEX = {k: v for k, v in INSTRUMENTS.items() if EXCHANGES[k[0]].kind is ExchangeKind.DEX}
INSTRUMENTS__CEX = {k: v for k, v in INSTRUMENTS.items() if EXCHANGES[k[0]].kind is ExchangeKind.CEX}
INSTRUMENTS__EXCHANGES = {}
for k in INSTRUMENTS.keys():
    e, i = k
    INSTRUMENTS__EXCHANGES[i] = {e} if i not in INSTRUMENTS__EXCHANGES else set([*INSTRUMENTS__EXCHANGES[i], e])


class InstrumentPrice(NamedTuple):
    buy: Decimal
    sell: Decimal


class LastPriceMessage(NamedTuple):
    exchange: Exchange
    instrument: Instrument
    price: InstrumentPrice

    def to_bytes(self) -> bytes:
        buy = str(self.price.buy).encode("ascii")
        sell = str(self.price.sell).encode("ascii")

        return bytes([
            self.exchange.value,
            *self.instrument.value.to_bytes(2, "little"),
            len(buy),
            *buy,
            len(sell),
            *sell
        ])

    @staticmethod
    def from_bytes(data: bytes) -> 'LastPriceMessage':
        buy_len = data[3]
        buy_s = data[4:4+buy_len].decode("ascii")
        sell_len = data[4+buy_len]
        sell_s = data[4+buy_len+1:4+buy_len+1+sell_len].decode("ascii")
        return LastPriceMessage(
            exchange=Exchange(data[0]),
            instrument=Instrument(int.from_bytes(data[1:2], "little")),
            price=InstrumentPrice(
                buy=Decimal(buy_s),
                sell=Decimal(sell_s),
            ),
        )
