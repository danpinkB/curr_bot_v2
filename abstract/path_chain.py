import json
from decimal import Decimal
from enum import Enum
from typing import NamedTuple, List

from abstract.instrument import Instrument


class QuoteType(Enum):
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
    instrument: Instrument
    version: str
    percent: float
    qtype: QuoteType
    pools: List[str]

    @staticmethod
    def from_cli(data: CLIQuoteUniswap, instrument: Instrument, qtype: QuoteType) -> List['PathChain']:
        return [
            PathChain(
                instrument=instrument,
                version=parts[0][1:-1],
                percent=float(parts[1][:-1]),
                pools=[pool[1:-1] for pool in parts[3:] if pool.startswith('[') and pool.endswith(']')],
                qtype=qtype
            )
            for parts in [entry.split(' ') for entry in data.best_route.split(', ')]
        ]

    def to_str(self) -> str:
        return json.dumps(self._asdict())

    @classmethod
    def from_str(cls, data: str) -> 'PathChain':
        return cls(**json.loads(data))
