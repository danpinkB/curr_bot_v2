from _decimal import Decimal
from enum import Enum, unique, IntEnum
from types import MappingProxyType

from eth_utils import to_checksum_address

from abstract.instrument import Instrument, CEXExchangeInstrumentParams, DEXExchangeInstrumentParams, \
    ExchangeInstrumentParams, ExchangeInstrument
from abstract.token import DEXToken, CEXToken
from abstract.exchange import ExchangeKind, Exchange, ExchangeParams

EXCHANGES = {
    Exchange.BINANCE: ExchangeParams(
        kind=ExchangeKind.CEX,
        icon='🔶',
        name="BIN"
    ),
    Exchange.UNISWAP: ExchangeParams(
        kind=ExchangeKind.DEX,
        icon='🦄',
        name="UNI"
    ),
}


@unique
class TokenDecimals(IntEnum):
    D18 = 1_000_000_000_000_000_000
    D16 = 1_000_000_000_000_000_0
    D8 = 100_000_000
    D9 = 1_000_000_000
    D6 = 1_000_000

@unique
class EthTokens(Enum):
    ETH = DEXToken(address=to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"), symbol="ETH", decimals=TokenDecimals.D18.value)
    ARB = DEXToken(address=to_checksum_address("0xB50721BCf8d664c30412Cfbc6cf7a15145234ad1"), symbol="ARB", decimals=TokenDecimals.D18.value)
    BTC = DEXToken(address=to_checksum_address("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"), symbol="BTC", decimals=TokenDecimals.D8.value)
    BEAM = DEXToken(address=to_checksum_address('0x62d0a8458ed7719fdaf978fe5929c6d342b0bfce'), symbol="BEAM", decimals=TokenDecimals.D18.value)
    PAXG = DEXToken(address=to_checksum_address('0x45804880de22913dafe09f4980848ece6ecbaf78'), symbol="PAXG", decimals=TokenDecimals.D18.value)
    PEPE = DEXToken(address=to_checksum_address('0x6982508145454ce325ddbe47a25d4ec3d2311933'), symbol="PEPE", decimals=TokenDecimals.D18.value)
    FLOKI = DEXToken(address=to_checksum_address('0xcf0c122c6b73ff809c693db761e7baebe62b6a2e'), symbol="FLOKI", decimals=TokenDecimals.D9.value)
    SUPER = DEXToken(address=to_checksum_address('0xe53ec727dbdeb9e2d5456c3be40cff031ab40a55'), symbol="SUPER", decimals=TokenDecimals.D18.value)

    XRP = DEXToken(address=to_checksum_address("0x39fBBABf11738317a448031930706cd3e612e1B9"), symbol="XRP", decimals=TokenDecimals.D18.value)
    SOL = DEXToken(address=to_checksum_address("0xD31a59c85aE9D8edEFeC411D448f90841571b89c"), symbol="SOL", decimals=TokenDecimals.D9.value)
    TON = DEXToken(address=to_checksum_address("0x582d872A1B094FC48F5DE31D3B73F2D9bE47def1"), symbol="TON", decimals=TokenDecimals.D9.value)

    # TRX = DEXToken(address=to_checksum_address("0x50327c6c5a14DCaDE707ABad2E27eB517df87AB5"), symbol="TRX", decimals=TokenDecimals.D9.value)
    MATIC = DEXToken(address=to_checksum_address("0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0"), symbol="MATIC", decimals=TokenDecimals.D18.value)
    UNI = DEXToken(address=to_checksum_address("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"), symbol="UNI", decimals=TokenDecimals.D18.value)
    BADGER = DEXToken(address=to_checksum_address("0x3472A5A71965499acd81997a54BBA8D852C6E53d"), symbol="BADGER", decimals=TokenDecimals.D18.value)
    SUSHI = DEXToken(address=to_checksum_address("0x6B3595068778DD592e39A122f4f5a5cF09C90fE2"), symbol="SUSHI", decimals=TokenDecimals.D18.value)
    INJ = DEXToken(address=to_checksum_address("0xe28b3B32B6c345A34Ff64674606124Dd5Aceca30"), symbol="INJ", decimals=TokenDecimals.D18.value)
    INCH = DEXToken(address=to_checksum_address("0x111111111117dC0aa78b770fA6A738034120C302"), symbol="1INCH", decimals=TokenDecimals.D18.value)
    NEXO = DEXToken(address=to_checksum_address("0xB62132e35a6c13ee1EE0f84dC5d40bad8d815206"), symbol="NEXO", decimals=TokenDecimals.D18.value)
    FET = DEXToken(address=to_checksum_address("0xaea46A60368A7bD060eec7DF8CBa43b7EF41Ad85"), symbol="FET", decimals=TokenDecimals.D18.value)
    APE = DEXToken(address=to_checksum_address("0x4d224452801ACEd8B2F0aebE155379bb5D594381"), symbol="APE", decimals=TokenDecimals.D18.value)
    POWR = DEXToken(address=to_checksum_address("0x595832F8FC6BF59c85C527fEC3740A1b7a361269"), symbol="POWR", decimals=TokenDecimals.D6.value)
    BOND = DEXToken(address=to_checksum_address("0x0391D2021f89DC339F60Fff84546EA23E337750f"), symbol="BOND", decimals=TokenDecimals.D18.value)
    USDT = DEXToken(address=to_checksum_address("0xdAC17F958D2ee523a2206206994597C13D831ec7"), symbol="USDT", decimals=TokenDecimals.D6.value)


NON_REQUIRED_CHECK_TOKENS = ["1INCH", 'BEAMX']

assert len(set(e.value.address for e in EthTokens)) == len(EthTokens)
for e in EthTokens:
    if e.value.symbol not in NON_REQUIRED_CHECK_TOKENS:
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
    BOND = CEXToken(symbol="BOND")
    USDT = CEXToken(symbol="USDT")
    BEAM = CEXToken(symbol="BEAMX")
    PAXG = CEXToken(symbol="PAXG")
    PEPE = CEXToken(symbol="PEPE")
    FLOKI = CEXToken(symbol="FLOKI")
    SUPER = CEXToken(symbol="SUPER")


BINANCE_STABLES = ("USDT")


for e in BinanceTokens:
    if e.value.symbol not in NON_REQUIRED_CHECK_TOKENS or e.value.symbol not in NON_REQUIRED_CHECK_TOKENS:
        assert e.name == e.value.symbol


INSTRUMENTS = MappingProxyType({
    ExchangeInstrument(Exchange.UNISWAP, Instrument.ETH__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.ETH.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.ARB__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.ARB.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.BTC__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.BTC.value, EthTokens.USDT.value)),
    # ExchangeInstrument(Exchange.UNISWAP, Instrument.XRP__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.XRP.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.SOL__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.SOL.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.TON__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.TON.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.MATIC__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.MATIC.value, EthTokens.USDT.value)),
    # ExchangeInstrument(Exchange.UNISWAP, Instrument.BADGER__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.BADGER.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.SUSHI__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.SUSHI.value, EthTokens.USDT.value)),
    # ExchangeInstrument(Exchange.UNISWAP, Instrument.INJ__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.INJ.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.INCH__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.INCH.value, EthTokens.USDT.value)),
    # ExchangeInstrument(Exchange.UNISWAP, Instrument.NEXO__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.NEXO.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.FET__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.FET.value, EthTokens.USDT.value)),
    # ExchangeInstrument(Exchange.UNISWAP, Instrument.APE__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.APE.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.POWR__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.POWR.value, EthTokens.USDT.value)),
    # ExchangeInstrument(Exchange.UNISWAP, Instrument.BOND__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.BOND.value, EthTokens.USDT.value)),
    #new
    ExchangeInstrument(Exchange.UNISWAP, Instrument.BEAM__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.BEAM.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.PAXG__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.PAXG.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.PEPE__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.PEPE.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.FLOKI__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.FLOKI.value, EthTokens.USDT.value)),
    ExchangeInstrument(Exchange.UNISWAP, Instrument.SUPER__USDT): ExchangeInstrumentParams(dex=DEXExchangeInstrumentParams(EthTokens.SUPER.value, EthTokens.USDT.value)),


    ExchangeInstrument(Exchange.BINANCE, Instrument.ETH__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.ETH.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.ARB__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.ARB.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.BTC__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.BTC.value, BinanceTokens.USDT.value)),
    # ExchangeInstrument(Exchange.BINANCE, Instrument.XRP__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.XRP.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.SOL__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.SOL.value, BinanceTokens.USDT.value)),
    # ExchangeInstrument(Exchange.BINANCE, Instrument.TON__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.TON.value, BinanceTokens.USDT.value)),
    # ExchangeInstrument(Exchange.BINANCE, Instrument.TRX__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.TRX.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.MATIC__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.MATIC.value, BinanceTokens.USDT.value)),
    # ExchangeInstrument(Exchange.BINANCE, Instrument.BADGER__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.BADGER.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.SUSHI__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.SUSHI.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.INJ__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.INJ.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.AAVE__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.AAVE.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.LQTY__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.LQTY.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.INCH__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.INCH.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.NEXO__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.NEXO.value, BinanceTokens.USDT.value)),
    # ExchangeInstrument(Exchange.BINANCE, Instrument.FET__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.FET.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.APE__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.APE.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.POWR__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.POWR.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.BOND__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.BOND.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.BEAM__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.BEAM.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.PAXG__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.PAXG.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.PEPE__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.PEPE.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.FLOKI__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.FLOKI.value, BinanceTokens.USDT.value)),
    ExchangeInstrument(Exchange.BINANCE, Instrument.SUPER__USDT): ExchangeInstrumentParams(cex=CEXExchangeInstrumentParams(BinanceTokens.SUPER.value, BinanceTokens.USDT.value)),
})

SYMBOL_INSTRUMENT = {}

for instrument in Instrument:
    base, quote = instrument.name.split("__")
    SYMBOL_INSTRUMENT[f'{base}{quote}'] = instrument
    SYMBOL_INSTRUMENT[f'{quote}{base}'] = instrument

SYMBOL_INSTRUMENT = MappingProxyType(SYMBOL_INSTRUMENT)


INSTRUMENTS_CONNECTIVITY = {}

for k, v in INSTRUMENTS.items():
    INSTRUMENTS_CONNECTIVITY[k.instrument] = tuple([*(INSTRUMENTS_CONNECTIVITY.get(k.instrument) or []), k])

INSTRUMENTS_CONNECTIVITY = MappingProxyType({k: v for k, v in INSTRUMENTS_CONNECTIVITY.items() if len(v) > 1})

k: ExchangeInstrument
v: ExchangeInstrumentParams
INSTRUMENTS__DEX = MappingProxyType({k: v for k, v in INSTRUMENTS.items() if k.exchange.kind is ExchangeKind.DEX})
INSTRUMENTS__CEX = MappingProxyType({k: v for k, v in INSTRUMENTS.items() if k.exchange.kind is ExchangeKind.CEX})

INSTRUMENTS__EXCHANGES = {}
for k in INSTRUMENTS.keys():
    e, i = k
    INSTRUMENTS__EXCHANGES[i] = {e} if i not in INSTRUMENTS__EXCHANGES else set([*INSTRUMENTS__EXCHANGES[i], e])

INSTRUMENTS__EXCHANGES = MappingProxyType(INSTRUMENTS__EXCHANGES)


ETH_INSTRUMENT_ADDRESS_PARAMS = {}
ei: ExchangeInstrument
eip: ExchangeInstrumentParams
for p in {eip.dex for ei, eip in INSTRUMENTS.items() if ei.exchange == Exchange.UNISWAP}:
    ETH_INSTRUMENT_ADDRESS_PARAMS[p.quote.address] = p.quote
    ETH_INSTRUMENT_ADDRESS_PARAMS[p.base.address] = p.base

ETH_INSTRUMENT_ADDRESS_PARAMS = MappingProxyType(ETH_INSTRUMENT_ADDRESS_PARAMS)
