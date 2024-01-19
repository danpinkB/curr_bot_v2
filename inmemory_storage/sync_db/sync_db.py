from aioredis import Redis

from inmemory_storage.sync_db.env import SYNC_DB__DSN


class SyncDB:
    def __init__(self, dsn: str):
        self._conn: Redis = Redis.from_url(dsn)

    async def lock_action(self, action_name: str, time_ms: int) -> None:
        await self._conn.psetex(action_name, time_ms, "LOCKED")

    async def is_lock(self, action_name: str) -> bool:
        return await self._conn.get(action_name)


def sync_db():
    return SyncDB(SYNC_DB__DSN)
