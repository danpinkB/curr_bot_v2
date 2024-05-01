from inmemory_storage.sync_db.env import SYNC_DB__DSN
from redis import asyncio as aioredis


class SyncDB:
    def __init__(self, dsn: str):
        self._conn = aioredis.from_url(dsn)

    async def lock_action(self, action_name: str, time_ms: int) -> None:
        await self._conn.psetex(action_name, time_ms, "LOCKED")

    async def is_lock(self, action_name: str) -> bool:
        return await self._conn.exists(action_name)

    async def infinite_lock(self, action_name: str) -> None:
        if self.is_lock(action_name):
            async with self._conn.pipeline() as pipe:
                await pipe.delete(action_name)
                await pipe.set(action_name, True)
        else:
            await self._conn.set(action_name, True)

    async def infinite_realize(self, action_name: str):
        await self._conn.delete(action_name)


def sync_db():
    return SyncDB(SYNC_DB__DSN)
