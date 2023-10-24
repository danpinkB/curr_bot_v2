from kv_db.common.sync_db_rconn import SyncDbRConnection
from kv_db.db_price_parser_uniswap_sync.env import DB_PRICE_PARSER_SYNC__DSN


class DbPriceParserUniswapSyncProvider(SyncDbRConnection):
    pass


def db_price_parser_uniswap_sync():
    return DbPriceParserUniswapSyncProvider(DB_PRICE_PARSER_SYNC__DSN)
