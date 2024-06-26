import redis
from redis.asyncio import Redis

from kv_db.db_tg_settings.structures import TelegramSettings

SETTINGS_KEY = "SETTINGS"


class TgSettingsProvider:
    def __init__(self, dsn: str):
        self._conn: Redis = redis.asyncio.from_url(dsn)

    async def is_connected(self) -> bool:
        await self._conn.ping()
        return True

    async def get_settings(self) -> TelegramSettings:
        settings_data = await self._conn.hgetall(SETTINGS_KEY)
        if len(settings_data) == 0:
            return TelegramSettings(
                percent=0.7,
                calc_volume=10_000,
                messages_delay=100
            )
        return TelegramSettings(*settings_data)

    async def set_settings(self, settings: TelegramSettings) -> None:
        async with self._conn.pipeline() as pipe:
            await pipe.hset(SETTINGS_KEY, "percent", str(settings.percent))
            await pipe.hset(SETTINGS_KEY, "messages_delay", str(settings.messages_delay))
            await pipe.hset(SETTINGS_KEY, "calc_volume", str(settings.calc_volume))
            await pipe.execute()
#
