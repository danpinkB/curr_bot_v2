from typing import Optional

from jinja2 import Template
from redis.backoff import ExponentialBackoff
from redis.client import Redis
from redis.exceptions import (
    BusyLoadingError,
    ConnectionError,
    TimeoutError
)
from redis.retry import Retry

from obs_shared.connection.common.base_r_conn import BaseRconn
from obs_shared.types.path_row import PathRow, PathRowChain

DEX_ROUTE_KEY = Template("route_{{exchange}}_{{pair}}")


class PathRConnection(BaseRconn):
    def __init__(self, dns_url: str):
        super().__init__(dns_url)
        
    def set_exchange_pair_path(self, ex: str, pair_symbol: str, path: PathRow, type_: str) -> None:
        self._conn.hset(DEX_ROUTE_KEY.render(exchange=ex, pair=pair_symbol), type_, path.to_string())

    def clear_exchange_pair_path(self, ex: str, pair_symbol: str, type_: str) -> None:
        self._conn.hdel(DEX_ROUTE_KEY.render(exchange=ex, pair=pair_symbol), type_)

    def get_exchange_pair_path(self, ex: str, pair_symbol: str, type_: str) -> Optional[PathRow]:
        path = self._conn.hget(DEX_ROUTE_KEY.render(exchange=ex, pair=pair_symbol), type_)
        return PathRow.from_string(path) if path is not None else None

