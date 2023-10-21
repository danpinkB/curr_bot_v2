from _decimal import Decimal
from enum import Enum, IntEnum, unique
from types import MappingProxyType
from typing import NamedTuple, Set, Optional, Tuple, Callable

from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address

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
        return EXCHANGES[self].kind


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


class DEXToken(NamedTuple):
    symbol: str
    address: ChecksumAddress
    decimals: Decimal


class CEXToken(NamedTuple):
    symbol: str

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

    def exchagnes(self) -> Set[Exchange]:
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

@unique
class TokenDecimals(Enum):
    D16 = Decimal(1000000000000000000)
    D8 = Decimal(100000000)
    D9 = Decimal(1000000000)
    D6 = Decimal(1000000)

@unique
class EthTokens(Enum):
    ETH = DEXToken(address=to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"), symbol="ETH", decimals=TokenDecimals.D16.value)
    ARB = DEXToken(address=to_checksum_address("0xB50721BCf8d664c30412Cfbc6cf7a15145234ad1"), symbol="ARB", decimals=TokenDecimals.D16.value)
    BTC = DEXToken(address=to_checksum_address("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"), symbol="BTC", decimals=TokenDecimals.D8.value)
    XRP = DEXToken(address=to_checksum_address("0x39fBBABf11738317a448031930706cd3e612e1B9"), symbol="XRP", decimals=TokenDecimals.D16.value)
    SOL = DEXToken(address=to_checksum_address("0xD31a59c85aE9D8edEFeC411D448f90841571b89c"), symbol="SOL", decimals=TokenDecimals.D9.value)
    TON = DEXToken(address=to_checksum_address("0x582d872A1B094FC48F5DE31D3B73F2D9bE47def1"), symbol="TON", decimals=TokenDecimals.D9.value)
    TRX = DEXToken(address=to_checksum_address("0x50327c6c5a14DCaDE707ABad2E27eB517df87AB5"), symbol="TRX", decimals=TokenDecimals.D9.value)
    MATIC = DEXToken(address=to_checksum_address("0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0"), symbol="MATIC", decimals=TokenDecimals.D16.value)
    UNI = DEXToken(address=to_checksum_address("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"), symbol="UNI", decimals=TokenDecimals.D16.value)
    BADGER = DEXToken(address=to_checksum_address("0x3472A5A71965499acd81997a54BBA8D852C6E53d"), symbol="BADGER", decimals=TokenDecimals.D16.value)
    SUSHI = DEXToken(address=to_checksum_address("0x6B3595068778DD592e39A122f4f5a5cF09C90fE2"), symbol="SUSHI", decimals=TokenDecimals.D16.value)
    INJ = DEXToken(address=to_checksum_address("0xe28b3B32B6c345A34Ff64674606124Dd5Aceca30"), symbol="INJ", decimals=TokenDecimals.D16.value)
    AAVE = DEXToken(address=to_checksum_address("0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9"), symbol="AAVE", decimals=TokenDecimals.D16.value)
    LQTY = DEXToken(address=to_checksum_address("0x6DEA81C8171D0bA574754EF6F8b412F2Ed88c54D"), symbol="LQTY", decimals=TokenDecimals.D16.value)
    INCH = DEXToken(address=to_checksum_address("0x111111111117dC0aa78b770fA6A738034120C302"), symbol="1INCH", decimals=TokenDecimals.D16.value)
    NEXO = DEXToken(address=to_checksum_address("0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206"), symbol="NEXO", decimals=TokenDecimals.D16.value)
    FET = DEXToken(address=to_checksum_address("0xaea46A60368A7bD060eec7DF8CBa43b7EF41Ad85"), symbol="FET", decimals=TokenDecimals.D16.value)
    APE = DEXToken(address=to_checksum_address("0x4d224452801ACEd8B2F0aebE155379bb5D594381"), symbol="APE", decimals=TokenDecimals.D16.value)
    POWR = DEXToken(address=to_checksum_address("0x595832F8FC6BF59c85C527fEC3740A1b7a361269"), symbol="POWR", decimals=TokenDecimals.D16.value)
    USDT = DEXToken(address=to_checksum_address("0xdAC17F958D2ee523a2206206994597C13D831ec7"), symbol="USDT", decimals=TokenDecimals.D6.value)


assert len(set(e.value.address for e in EthTokens)) == len(EthTokens)
for e in EthTokens:
    assert e.name == e.value.symbol


class BinanceTokens(Enum):
    ETH = CEXToken(symbol="ETH")
    ARB = CEXToken(symbol="ARB")
    BTC = CEXToken(symbol="BTC")
    XRP = CEXToken(symbol="XRP")
    SOL = CEXToken(symbol="SOL")
    TON = CEXToken(symbol="TON")
    TRX = CEXToken(symbol="TRX")
    MATIC = CEXToken(symbol="MATIC")
    UNI = CEXToken(symbol="UNI")
    BADGER = CEXToken(symbol="BADGER")
    SUSHI = CEXToken(symbol="SUSHI")
    INJ = CEXToken(symbol="INJ")
    AAVE = CEXToken(symbol="AAVE")
    LQTY = CEXToken(symbol="LQTY")
    INCH = CEXToken(symbol="1INCH")
    NEXO = CEXToken(symbol="NEXO")
    FET = CEXToken(symbol="FET")
    APE = CEXToken(symbol="APE")
    POWR = CEXToken(symbol="POWR")
    USDT = CEXToken(symbol="USDT")


for e in BinanceTokens:
    assert e.name == e.value.symbol


class ExchangeInstrument(NamedTuple):
    exchange: Exchange
    instrument: Instrument


INSTRUMENTS = MappingProxyType({
    ExchangeInstrument(Exchange.UNISWAP, Instrument.ETH__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.ETH.value, EthTokens.USDT.value)),

})

INSTRUMENTS_CONNECTIVITY = {}

for k, v in INSTRUMENTS.items():
    INSTRUMENTS_CONNECTIVITY[k.instrument] = tuple([*(INSTRUMENTS_CONNECTIVITY.get(k.instrument) or []), k])


INSTRUMENTS_CONNECTIVITY = MappingProxyType({k: v for k, v in INSTRUMENTS_CONNECTIVITY if len(v) > 1})

INSTRUMENTS__DEX = MappingProxyType({k: v for k, v in INSTRUMENTS.items() if k.exchange.kind is ExchangeKind.DEX})
INSTRUMENTS__CEX = MappingProxyType({k: v for k, v in INSTRUMENTS.items() if k.exchange.kind is ExchangeKind.CEX})

INSTRUMENTS__EXCHANGES = {}
for k in INSTRUMENTS.keys():
    e, i = k
    INSTRUMENTS__EXCHANGES[i] = {e} if i not in INSTRUMENTS__EXCHANGES else set([*INSTRUMENTS__EXCHANGES[i], e])

INSTRUMENTS__EXCHANGES = MappingProxyType(INSTRUMENTS__EXCHANGES)


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
