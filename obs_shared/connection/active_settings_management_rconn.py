from typing import Optional, Set

from jinja2 import Template

from obs_shared.connection.common.base_r_conn import BaseRconn
from obs_shared.types.comparer_settings import ComparerSettings

EX_BANNED_PAIRS_KEY = Template("{{exchange}}_banned_pairs")
EX_ACTIVE_PAIRS_KEY = Template("{{exchange}}_active_pairs")

SETTINGS_KEY = "SETTINGS"


class ActiveSettingsManagementRConnection(BaseRconn):
    EXCHANGES_KEY = "exchanges"
    GROUPS_KEY = Template("{{group}}_exchanges")

    def __init__(self, dns_url: str):
        super().__init__(dns_url)

    def is_connected(self) -> bool:
        self._conn.ping()
        return True

    def get_exchanges(self) -> Set[str]:
        return self._conn.smembers(self.EXCHANGES_KEY)

    def get_exchange_pairs(self, exchange: str) -> Set[str]:
        return self._conn.smembers(EX_ACTIVE_PAIRS_KEY.render(exchange=exchange))

    def get_exchange_banned_pairs(self, exchange: str) -> Set[str]:
        return self._conn.smembers(EX_BANNED_PAIRS_KEY.render(exchange=exchange))

    def activate_ex_pair(self, exchange: str, pair_symbol: str) -> None:
        with self._conn.pipeline() as pipe:
            pipe.srem(EX_BANNED_PAIRS_KEY.render(exchange=exchange), pair_symbol)
            pipe.sadd(EX_ACTIVE_PAIRS_KEY.render(exchange=exchange), pair_symbol)
            pipe.execute()

    def activate_ex_pairs(self, exchange: str, pair_symbols: Set[str]) -> None:
        with self._conn.pipeline() as pipe:
            for pair_symbol in pair_symbols:
                pipe.srem(EX_BANNED_PAIRS_KEY.render(exchange=exchange), pair_symbol)
                pipe.sadd(EX_ACTIVE_PAIRS_KEY.render(exchange=exchange), pair_symbol)
            pipe.execute()

    def deactivate_ex_pair(self, exchange: str, pair_symbol: str) -> None:
        with self._conn.pipeline() as pipe:
            pipe.sadd(EX_BANNED_PAIRS_KEY.render(exchange=exchange), pair_symbol)
            pipe.srem(EX_ACTIVE_PAIRS_KEY.render(exchange=exchange), pair_symbol)
            pipe.execute()

    def deactivate_ex_pairs(self, exchange: str, pair_symbols: Set[str]) -> None:
        with self._conn.pipeline() as pipe:
            for pair_symbol in pair_symbols:
                pipe.sadd(EX_BANNED_PAIRS_KEY.render(exchange=exchange), pair_symbol)
                pipe.srem(EX_ACTIVE_PAIRS_KEY.render(exchange=exchange), pair_symbol)
            pipe.execute()

    def get_setting(self) -> ComparerSettings:
        settings = self._conn.hgetall(SETTINGS_KEY)
        if len(settings) == 0:
            self.set_settings(ComparerSettings(
                percent=0.5,
                delay_mills=200,
                rvolume=10000,
                mdelay=60*2
            ))
        return ComparerSettings.from_row(tuple[str, str, str, str](settings.values()))

    def set_setting(self, setting_name: str, setting_value: str) -> None:
        if setting_name in ComparerSettings.keys():
            self._conn.hset(SETTINGS_KEY, setting_name, setting_value)

    def set_settings(self, settings: ComparerSettings) -> None:
        with self._conn.pipeline() as pipe:
            pipe.hset(SETTINGS_KEY, "percent", str(settings.percent))
            pipe.hset(SETTINGS_KEY, "delay_mills", str(settings.delay_mills))
            pipe.hset(SETTINGS_KEY, "rvolume", str(settings.rvolume))
            pipe.hset(SETTINGS_KEY, "mdelay", str(settings.mdelay))
            pipe.execute()

    def get_group_exchanges(self, group: int) -> Set[str]:
        return self._conn.smembers(self.GROUPS_KEY.render(group=group))

