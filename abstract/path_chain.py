import json
import logging
from decimal import Decimal
from enum import Enum, IntEnum
from typing import NamedTuple, List

from abstract.instrument import Instrument


class QuoteType(IntEnum):
    exactIn = 0
    exactOut = 1


class CLIQuoteUniswap(NamedTuple):
    best_route: str
    quote_in: Decimal
    gas_quote: Decimal
    gas_usd: Decimal
    call_data: str
    block_number: int


class PathChain(NamedTuple):
    version: str
    percent: float
    pools: List[str]


class InstrumentRoute(NamedTuple):
    instrument: Instrument
    qtype: QuoteType
    pathes: List[PathChain]

    @staticmethod
    def from_cli(data: CLIQuoteUniswap, instrument: Instrument, qtype: QuoteType) -> 'InstrumentRoute':
        # logging.info(data)
        return InstrumentRoute(
            instrument=instrument,
            qtype=qtype,
            pathes=[
                PathChain(
                    version=parts[0][1:-1],
                    percent=float(parts[1][:-1]),
                    pools=[pool[1:-1] for pool in parts[3:] if pool.startswith('[') and pool.endswith(']')],
                )
                for parts in [entry.split(' ') for entry in data.best_route.split(', ')]
            ]
        )

    def to_str(self) -> str:
        return json.dumps(self._asdict())

    @classmethod
    def from_str(cls, data: str) -> 'InstrumentRoute':
        return cls(**json.loads(data))
