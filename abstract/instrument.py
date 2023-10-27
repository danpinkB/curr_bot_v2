from enum import unique, Enum
from typing import Set, NamedTuple, Optional

from abstract.exchange import Exchange
from abstract.token import CEXToken, DEXToken


@unique
class Instrument(Enum):
    ETH__USDT = 1
    ARB__USDT = 2
    BTC__USDT = 3
    XRP__USDT = 4
    SOL__USDT = 5
    TON__USDT = 6
    TRX__USDT = 7
    MATIC__USDT = 8
    UNI__USDT = 9
    BADGER__USDT = 10
    SUSHI__USDT = 11
    INJ__USDT = 12
    AAVE__USDT = 13
    LQTY__USDT = 14
    INCH__USDT = 15
    NEXO__USDT = 16
    FET__USDT = 17
    APE__USDT = 18
    POWR__USDT = 19
    BOND__USDT = 20

    def exchagnes(self) -> Set[Exchange]:
        from abstract.const import INSTRUMENTS__EXCHANGES
        return INSTRUMENTS__EXCHANGES[self]


class CEXExchangeInstrumentParams(NamedTuple):
    base: CEXToken
    quote: CEXToken


class DEXExchangeInstrumentParams(NamedTuple):
    base: DEXToken
    quote: DEXToken


class ExchangeInstrumentParams(NamedTuple):
    cex: Optional[CEXExchangeInstrumentParams] = None
    dex: Optional[DEXExchangeInstrumentParams] = None


class InstrumentParams(NamedTuple):
    pass


class ExchangeInstrument(NamedTuple):
    exchange: Exchange
    instrument: Instrument