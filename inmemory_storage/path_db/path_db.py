from typing import Optional

from redis.asyncio import Redis

from abstract.instrument import Instrument
from abstract.path_chain import QuoteType, InstrumentRoute
from inmemory_storage.path_db.env import PATH_DB__DSN


class PathDB:
    def __init__(self, dsn: str):
        self._conn: Redis = Redis.from_url(dsn)

    async def set_route(self, chain: InstrumentRoute) -> None:
        await self._conn.set(f'{chain.instrument.value}{chain.qtype.value}', chain.to_bytes())

    async def get_route(self, instrument: Instrument, qtype: QuoteType) -> Optional[InstrumentRoute]:
        path = await self._conn.get(f'{instrument.value}{qtype.value}')
        if path:
            return InstrumentRoute.from_bytes(path)


def path_db():
    return PathDB(PATH_DB__DSN)
