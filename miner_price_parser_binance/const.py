from typing import Tuple, Dict

from abstract.const import INSTRUMENTS, INSTRUMENTS_CONNECTIVITY
from abstract.exchange import Exchange
from abstract.instrument import Instrument, ExchangeInstrument

REQUIRED_INSTRUMENTS: Tuple[Instrument, ...] = tuple(k for k, v in INSTRUMENTS_CONNECTIVITY.items() if any(ei.exchange == Exchange.BINANCE for ei in v))
SYMBOL_INSTRUMENT: Dict[str, Instrument] = {
    INSTRUMENTS[ExchangeInstrument(Exchange.BINANCE, i)].cex.base.symbol + INSTRUMENTS[ExchangeInstrument(Exchange.BINANCE, i)].cex.quote.symbol: i
    for i in REQUIRED_INSTRUMENTS
}
