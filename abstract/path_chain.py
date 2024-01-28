import pickle
from decimal import Decimal
from enum import IntEnum
from typing import NamedTuple, Tuple, Final

from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address

from abstract.const import ETH_INSTRUMENT_ADDRESS_PARAMS
from abstract.instrument import Instrument
from abstract.token import DEXToken


class QuoteType(IntEnum):
    exactIn = 0
    exactOut = 1


UNI_POOL_DATA_TYPE: Final = Tuple[str, str, str, int]
PATH_CHAIN_DATA_TYPE: Final = Tuple[str, int, Tuple[UNI_POOL_DATA_TYPE, ...]]
INSTRUMENT_ROUTE_DATA_TYPE: Final = Tuple[int, int, Tuple[PATH_CHAIN_DATA_TYPE, ...]]


class UniPool(NamedTuple):
    address: ChecksumAddress
    token_from: ChecksumAddress
    token_to: ChecksumAddress
    fee: int

    # @property
    # def instrument_params_token_from(self) -> DEXToken:
    #     return ETH_INSTRUMENT_ADDRESS_PARAMS[self.token_from]

    # @property
    # def instrument_params_token_to(self) -> DEXToken:
    #     return ETH_INSTRUMENT_ADDRESS_PARAMS[self.token_from]

    @classmethod
    def from_data(cls, data: UNI_POOL_DATA_TYPE):
        return cls(
            address=to_checksum_address(data[0]),
            token_from=to_checksum_address(data[1]),
            token_to=to_checksum_address(data[2]),
            fee=data[3]
        )

    def to_data(self) -> UNI_POOL_DATA_TYPE:
        return str(self.address), str(self.token_from), str(self.token_to), self.fee


class RouteChain(NamedTuple):
    version: str
    amount: int
    pools: Tuple[UniPool, ...]

    @classmethod
    def from_data(cls, data: PATH_CHAIN_DATA_TYPE) -> 'RouteChain':
        return cls(
            version=data[0],
            amount=data[1],
            pools=tuple(UniPool.from_data(pool) for pool in data[2])
        )

    def to_data(self) -> PATH_CHAIN_DATA_TYPE:
        return self.version, self.amount, tuple(pool.to_data() for pool in self.pools)


class InstrumentRoute(NamedTuple):
    instrument: Instrument
    qtype: QuoteType
    pathes: Tuple[RouteChain, ...]

    @classmethod
    def from_data(cls, route_data: INSTRUMENT_ROUTE_DATA_TYPE):
        return cls(Instrument(route_data[0]), QuoteType(route_data[1]), tuple(RouteChain.from_data(path) for path in route_data[2]))

    def to_data(self) -> INSTRUMENT_ROUTE_DATA_TYPE:
        return self.instrument, self.qtype, tuple(path.to_data() for path in self.pathes)

    def to_bytes(self) -> bytes:
        return pickle.dumps((self.to_data()))

    @classmethod
    def from_bytes(cls, data: bytes) -> 'InstrumentRoute':
        return cls.from_data(pickle.loads(data))

