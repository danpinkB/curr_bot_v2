from typing import Set

from jinja2 import Template

from obs_shared.connection.active_settings_management_rconn import ActiveSettingsManagementRConnection

GROUPS_KEY = Template("{{group}}_exchanges")


class ActiveSettingsExchangeRConnection(ActiveSettingsManagementRConnection):

    def __init__(self, dns_url: str, exchange: str, group: int):
        super().__init__(dns_url)
        self.add_exchange(exchange, group)
        self._exchange = exchange

    def is_connected(self) -> bool:
        self._conn.ping()
        return True

    def add_exchange(self, exchange: str, group: int) -> None:
        with self._conn.pipeline() as pipe:
            pipe.sadd(GROUPS_KEY.render(group=group), exchange)
            pipe.sadd(self.EXCHANGES_KEY, exchange)
            pipe.execute()

    def activate_pairs(self, pair_symbols: Set[str]) -> None:
        self.activate_ex_pairs(self._exchange, pair_symbols)

    def deactivate_pairs(self, pair_symbols: Set[str]) -> None:
        self.deactivate_ex_pairs(self._exchange, pair_symbols)

    def remove_pair(self, pair_symbol: str) -> None:
        self.remove_pair(pair_symbol)

    def get_pairs(self) -> Set[str]:
        return self.get_exchange_pairs(self._exchange)

    def get_banned_pairs(self) -> Set[str]:
        return self.get_exchange_banned_pairs(self._exchange)

    def get_group_exchanges(self, group: int) -> Set[str]:
        return self._conn.smembers(GROUPS_KEY.render(group=group))
