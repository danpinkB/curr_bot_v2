from redis import Redis, BusyLoadingError
from redis.backoff import ExponentialBackoff
from redis.retry import Retry


class BaseRconn:
    def __init__(self, dns_url: str) -> None:
        self._conn: Redis = Redis.from_url(dns_url,
                       decode_responses=True,
                       retry=Retry(ExponentialBackoff(), 5),
                       retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError])
