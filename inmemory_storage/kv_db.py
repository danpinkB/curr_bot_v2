from redis.asyncio import Redis

from inmemory_storage.env import KV_DB__DSN


class KvDB:
    def __init__(self, dsn: str):
        self._conn: Redis = Redis.from_url(dsn)

    async def set(self, key: str, value: str) -> None:
        await self._conn.set(key, value)

    async def get(self, key: str) -> str:
        return await self._conn.get(key)


def kv_db():
    return KvDB(KV_DB__DSN)
