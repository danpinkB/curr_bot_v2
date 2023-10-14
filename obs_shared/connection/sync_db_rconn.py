from obs_shared.connection.common.base_r_conn import BaseRconn


class SyncRConnection(BaseRconn):
    def __init__(self, dns_url: str):
        super().__init__(dns_url)

    def lock_action(self, action_name: str, expiration_time: int) -> None:
        with self._conn.pipeline() as pipe:
            pipe.hset(action_name, "LOCKED", "True")
            pipe.expire(action_name, expiration_time)
            pipe.execute()

    def is_lock(self, action_name: str) -> bool:
        return self._conn.hget(action_name, "LOCKED") is not None


