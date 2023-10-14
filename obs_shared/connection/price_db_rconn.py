import logging
from typing import Optional, Dict

from jinja2 import Template

from obs_shared.connection.common.base_r_conn import BaseRconn
from obs_shared.types.price_row import PriceRow

PRICE_HASH_TABLE_KEY = "prices"
EXCHANGE_PAIRS_KEY = Template("{{exchange}}_pairs")
EXCHANGE_PAIR_PRICE_KEY = Template("price_{{exchange}}_{{pair}}")
PAIR_EXCHANGES_PRICE_KEY = Template("price_{{pair}}")


class PriceRConnection(BaseRconn):
    def __init__(self, dns_url: str):
        super().__init__(dns_url)

    def set_exchange_pair_price(self, exchange: str, pair_symbol: str, price: PriceRow) -> None:
        with self._conn.pipeline() as pipe:
            pipe.hset(PRICE_HASH_TABLE_KEY, EXCHANGE_PAIR_PRICE_KEY.render(exchange=exchange, pair=pair_symbol),
                      price.to_row())
            pipe.sadd(PAIR_EXCHANGES_PRICE_KEY.render(pair=pair_symbol), exchange)
            pipe.sadd(EXCHANGE_PAIRS_KEY.render(exchange=exchange), pair_symbol)
            pipe.execute()

    def clear_exchange_pair_price(self, exchange: str, pair_symbol: str) -> None:
        with self._conn.pipeline() as pipe:
            pipe.hdel(PRICE_HASH_TABLE_KEY, EXCHANGE_PAIR_PRICE_KEY.render(exchange=exchange, pair=pair_symbol))
            pipe.srem(PAIR_EXCHANGES_PRICE_KEY.render(pair=pair_symbol), exchange)
            pipe.srem(EXCHANGE_PAIRS_KEY.render(exchange=exchange), pair_symbol)
            pipe.execute()

    def get_exchange_pair_price(self, ex: str, pair_symbol: str) -> Optional[PriceRow]:
        price = self._conn.hget(PRICE_HASH_TABLE_KEY, EXCHANGE_PAIR_PRICE_KEY.render(exchange=ex, pair=pair_symbol))
        logging.info(f"price {price} {ex} {pair_symbol}")
        return PriceRow.from_row(price) if price is not None else None

    def get_pair_exchanges_prices(self, pair_symbol: str) -> Dict[str, Optional[PriceRow]]:
        return {exchange: self.get_exchange_pair_price(exchange, pair_symbol) for exchange in self._conn.smembers(PAIR_EXCHANGES_PRICE_KEY.render(pair=pair_symbol))}

    def get_exchange_pairs_prices(self, exchange: str) -> Dict[str, Optional[PriceRow]]:
        return {pair_symbol: self.get_exchange_pair_price(exchange, pair_symbol) for pair_symbol in self._conn.smembers(EXCHANGE_PAIRS_KEY.render(exchange=exchange))}
