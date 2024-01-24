from typing import Optional

from redis.asyncio import Redis

from abstract.instrument import Instrument
from abstract.path_chain import PathChain, QuoteType, InstrumentRoute
from path_parser_uniswap.env import PATH_DB__DSN


class PathDB:
    def __init__(self, dsn: str):
        self._conn: Redis = Redis.from_url(dsn)

    async def set_path(self, chain: InstrumentRoute) -> None:
        await self._conn.set(f'{chain.instrument.name}{chain.qtype.name}', chain.to_str())

    async def get_path(self, instrument: Instrument, qtype: QuoteType) -> Optional[InstrumentRoute]:
        path = await self._conn.get(f'{instrument.name}{qtype.name}')
        if path:
            return InstrumentRoute.from_str(path)


def path_db():
    return PathDB(PATH_DB__DSN)
