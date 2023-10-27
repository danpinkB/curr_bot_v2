from typing import Coroutine

from aioredis import Redis


class SyncDbRConnection:
    def __init__(self, dsn: str):
        self._conn: Redis = Redis.from_url(dsn)

    async def lock_action(self, action_name: str, time_ms: int) -> Coroutine[None]:
        return await self._conn.psetex(action_name, time_ms, "LOCKED")

    async def is_lock(self, action_name: str) -> Coroutine[bool]:
        return await self._conn.get(action_name)


