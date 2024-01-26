import json
import logging
from collections import namedtuple
from decimal import Decimal
from enum import Enum, IntEnum
from typing import NamedTuple, List, Tuple, Optional, Any

from abstract.instrument import Instrument, DEXExchangeInstrumentParams


class QuoteType(IntEnum):
    exactIn = 0
    exactOut = 1


class UniPool(NamedTuple):
    address: str
    token_from: str
    token_to: str
    fee: float

    @classmethod
    def from_list(cls, data: List[str, str, str, float]):
        return cls(*data)

    def to_list(self) -> Tuple[str, str, str, float]:
        return self.address, self.token_from, self.token_to, self.fee


class PathChain(NamedTuple):
    version: str
    amount: float
    pools: Tuple[UniPool, ...]

    @classmethod
    def from_list(cls, data: Tuple[str, float, List[Any]]):
        return cls(data[0], data[1], tuple(UniPool.from_list(pool) for pool in data[3]))

    def to_list(self) -> Tuple[str, float, Tuple[Any, ...]]:
        return self.version, self.amount, tuple(pool.to_list() for pool in self.pools)


class InstrumentRoute(NamedTuple):
    instrument: Instrument
    qtype: QuoteType
    pathes: Tuple[PathChain, ...]

    @classmethod
    def from_list(cls, route_data: Tuple[int, int, List[Any]]):
        return cls(Instrument(route_data[0]), QuoteType(route_data[1]), tuple(PathChain.from_list(path) for path in route_data[2]))

    def to_list(self) -> Tuple[int, int, Tuple[Any, ...]]:
        return self.instrument, self.qtype, tuple(path.to_list() for path in self.pathes)

    def to_string(self) -> str:
        return str(self.to_list())

    @classmethod
    def from_string(cls, input_string: str) -> 'InstrumentRoute':
        return cls.from_list(eval(input_string))

