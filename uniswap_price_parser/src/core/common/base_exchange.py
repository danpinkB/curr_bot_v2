from _decimal import Decimal
from abc import abstractmethod
from typing import Set

from obs_shared.types import TokenRow


class BaseExchange:
    @abstractmethod
    def parse_path(self, pair_symbol: str, token0: TokenRow, token1: TokenRow, type_: str) -> Set[str]:
        pass

    @abstractmethod
    def parse_price(
        self,
        token0: TokenRow,
        token1: TokenRow,
        is_buy: bool,
        path: dict
    ) -> Decimal:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
