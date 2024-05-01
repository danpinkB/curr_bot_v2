from redis.asyncio import Redis
from inmemory_storage.tg_settings_db.structures import TelegramSettings

SETTINGS_KEY = "SETTINGS"


class TgSettingsProvider:
    def __init__(self, dsn: str):
        self._conn: Redis = Redis.from_url(dsn)

    async def is_connected(self) -> bool:
        await self._conn.ping()
        return True

    async def get_settings(self) -> TelegramSettings:
        settings_data = await self._conn.hgetall(SETTINGS_KEY)
        if len(settings_data) != 3:
            return TelegramSettings(
                percent=0.01,
                calc_volume=10000,
                messages_delay=60
            )
        return TelegramSettings(
            percent=float(settings_data[b'percent']),
            calc_volume=int(settings_data[b'calc_volume']),
            messages_delay=int(settings_data[b'messages_delay']),
        )

    async def set_settings(self, settings: TelegramSettings) -> None:
        await self._conn.hset(SETTINGS_KEY, None, None, settings.model_dump())
        # async with self._conn.pipeline() as pipe:
        #     await pipe.hset(SETTINGS_KEY, "percent", str(settings.percent))
        #     await pipe.hset(SETTINGS_KEY, "messages_delay", str(settings.messages_delay))
        #     await pipe.hset(SETTINGS_KEY, "calc_volume", str(settings.calc_volume))
        #     await pipe.execute()
#
