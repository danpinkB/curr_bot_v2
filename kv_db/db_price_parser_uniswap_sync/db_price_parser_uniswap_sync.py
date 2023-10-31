import logging

import redis
from redlock import Redlock

from abstract.instrument import Instrument
from kv_db.db_price_parser_uniswap_sync.env import DB_PRICE_PARSER_SYNC__DSN


class DbPriceParserUniswapSyncProvider:
    def __init__(self, dsn: str):
        self._conn = Redlock([redis.from_url(dsn)])

    def is_unlocked(self, instrument: Instrument, ttl: int) -> bool:
        return not isinstance(self._conn.lock(instrument.name, ttl), bool)


def db_price_parser_uniswap_sync() -> DbPriceParserUniswapSyncProvider:
    return DbPriceParserUniswapSyncProvider(DB_PRICE_PARSER_SYNC__DSN)
