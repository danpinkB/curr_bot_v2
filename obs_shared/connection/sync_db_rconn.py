from datetime import timedelta

from obs_shared.connection.common.base_r_conn import BaseRconn


class SyncRConnection(BaseRconn):
    def __init__(self, dns_url: str):
        super().__init__(dns_url)

    def lock_action(self, action_name: str, time_ms: int) -> None:
        self._conn.psetex(action_name, time_ms, "LOCKED")

    def is_lock(self, action_name: str) -> bool:
        return self._conn.get(action_name)


