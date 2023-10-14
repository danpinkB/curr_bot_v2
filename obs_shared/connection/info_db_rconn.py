import logging
from typing import Set, Optional

from jinja2 import Template
from redis.client import Pipeline

from obs_shared.connection.common.base_r_conn import BaseRconn
from obs_shared.types.pair_row import PairRow
from obs_shared.types.token_row import TokenRow

EX_PAIRS_KEY = Template("{{exchange}}_pairs")
PAIR_EXES_KEY = Template("{{chain}}_{{pair}}_exchanges")

TOKENS_SYMBOLS_KEY = Template("{{chain}}_token")
TOKENS_KEY = Template("{{chain}}_{{address}}_info")
PAIRS_KEY = Template("{{chain}}_{{pair}}_info")


class InfoSettingsRConnection(BaseRconn):
    def __init__(self, dns_url: str, exchange: str, chain: Optional[int] = None):
        super().__init__(dns_url)
        self._chain_key = exchange if chain is None else chain

    def is_connected(self) -> bool:
        self._conn.ping()
        return True

    def remove_ex_pair(self, exchange: str, symbol: str, ) -> None:
        with self._conn.pipeline() as pipe:
            pipe.srem(EX_PAIRS_KEY.render(exchange=exchange), symbol)
            pipe.srem(PAIR_EXES_KEY.render(pair=symbol, chain=self._chain_key), exchange)
            pipe.execute()

    def remove_ex_pairs(self, exchange: str, pair_symbols: Set[str]) -> None:
        if len(pair_symbols) > 0:
            with self._conn.pipeline() as pipe:
                for pair_symbol in pair_symbols:
                    pipe.srem(EX_PAIRS_KEY.render(exchange=exchange), pair_symbol)
                    pipe.srem(PAIR_EXES_KEY.render(pair=pair_symbols, chain=self._chain_key), exchange)
                pipe.execute()

    def add_ex_pair(self, exchange: str, pair_symbol: str) -> None:
        with self._conn.pipeline() as pipe:
            pipe.sadd(EX_PAIRS_KEY.render(exchange=exchange), pair_symbol)
            pipe.sadd(PAIR_EXES_KEY.render(pair=pair_symbol, chain=self._chain_key), exchange)
            pipe.execute()

    def add_ex_pairs(self, exchange: str, pair_symbols: Set[str]) -> None:
        with self._conn.pipeline() as pipe:
            for pair_symbol in pair_symbols:
                pipe.sadd(EX_PAIRS_KEY.render(exchange=exchange), pair_symbol)
                pipe.sadd(PAIR_EXES_KEY.render(pair=pair_symbol, chain=self._chain_key), exchange)
            pipe.execute()

    def get_ex_pairs(self, exchange: str) -> Set[str]:
        return self._conn.smembers(EX_PAIRS_KEY.render(exchange=exchange))

    def get_pair_exes(self, pair_symbol: str) -> Set[str]:
        return self._conn.smembers(PAIR_EXES_KEY.render(pair=pair_symbol, chain=self._chain_key))

    def set_pair_info(self, pair_row: PairRow) -> None:
        with self._conn.pipeline() as pipe:
            pair_key = PAIRS_KEY.render(chain=pair_row.chain, pair=pair_row.symbol)
            pipe.hset(pair_key, "symbol", pair_row.symbol)
            pipe.hset(pair_key, "token0", pair_row.token0)
            pipe.hset(pair_key, "token1", pair_row.token1)
            pipe.hset(pair_key, "chain", str(pair_row.chain))
            pipe.execute()

    def set_token_info(self, token: TokenRow):
        with self._conn.pipeline() as pipe:
            self._set_token_info(token, pipe)
            pipe.execute()

    def get_pair_info(self, pair_symbol: str) -> PairRow:
        pair_key = PAIRS_KEY.render(chain=self._chain_key, pair=pair_symbol)
        pair_raw_info = self._conn.hgetall(pair_key)
        logging.info(f'{pair_symbol} {pair_key} {pair_raw_info}')
        return PairRow.from_row(tuple[str, str, str, int](pair_raw_info.values()))

    @staticmethod
    def _set_token_info(token_row: TokenRow, pipe: Pipeline) -> None:
        key = TOKENS_KEY.render(chain=token_row.chain, address=token_row.address)
        pipe.hset(key, "address", str(token_row.address))
        pipe.hset(key, "symbol", str(token_row.symbol))
        pipe.hset(key, "full_symbol", str(token_row.full_symbol))
        pipe.hset(key, "decimals", str(token_row.decimals))
        pipe.hset(key, "chain", str(token_row.chain))
        pipe.hset(TOKENS_SYMBOLS_KEY.render(chain=token_row.chain), token_row.symbol, token_row.address)

    def get_token_info_by_symbol(self, symbol: str) -> TokenRow:
        token_address = self._conn.hget(TOKENS_SYMBOLS_KEY.render(chain=self._chain_key), symbol)
        return TokenRow.from_row(
            tuple[str, str, str, str, int](
                self._conn.hgetall(TOKENS_KEY.render(chain=self._chain_key, address=token_address)).values()))

    def get_token_info_by_address(self, address: str) -> TokenRow:
        return TokenRow.from_row(
            tuple[str, str, str, str, int](
                self._conn.hgetall(TOKENS_KEY.render(chain=self._chain_key, address=address)).values()))
