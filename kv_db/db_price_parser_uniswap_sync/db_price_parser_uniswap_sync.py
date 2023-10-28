from typing import Coroutine

import redis.asyncio
from redis.asyncio import Redis

from abstract.instrument import Instrument
from kv_db.db_price_parser_uniswap_sync.env import DB_PRICE_PARSER_SYNC__DSN


class DbPriceParserUniswapSyncProvider:
    def __init__(self, dsn: str):
        self._conn: Redis = redis.asyncio.from_url(dsn)

    async def is_locked(self, instrument: Instrument) -> bool:
        locked_data = await self._conn.get(instrument.name)
        if locked_data is None:
            await self._conn.psetex(instrument.name, 1000, "LOCK")
        return locked_data is not None


def db_price_parser_uniswap_sync() -> DbPriceParserUniswapSyncProvider:
    return DbPriceParserUniswapSyncProvider(DB_PRICE_PARSER_SYNC__DSN)
