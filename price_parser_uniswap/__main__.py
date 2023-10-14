import logging
import time
from _decimal import Decimal

import web3
from jinja2 import Template

from obs_shared.connection.active_settings_exchange_rconn import ActiveSettingsExchangeRConnection
from obs_shared.connection.info_db_rconn import InfoSettingsRConnection
from obs_shared.connection.path_db_rconn import PathRConnection
from obs_shared.connection.price_db_rconn import PriceRConnection
from obs_shared.connection.rabbit_mq_connection import RMQConnection
from obs_shared.connection.sync_db_rconn import SyncRConnection
from obs_shared.static import uni_v3_quoter_abi
from obs_shared.types.calculation_price import CalculationPrice
from obs_shared.types.path_row import PathRow
from obs_shared.types.price_row import PriceRow
from obs_shared.types.token_row import TokenRow
from price_parser_uniswap.const import UNI_V3_QUOTER_ADDRESS, CHAIN
from price_parser_uniswap.env import REDIS_DSN__INFO, REDIS_DSN__PATH, REDIS_DSN__PRICE, JSON_RPC_PROVIDER, \
    REDIS_DSN__SYNC, RABBITMQ_QUE__SENDER, REDIS_DSN__SETTINGS, RMQ_HOST, RMQ_USER, RMQ_PASSWORD

NAME = "UNIv3"
_key = Template("{{pair}}_price_{{type}}")

setting_rconn: ActiveSettingsExchangeRConnection = ActiveSettingsExchangeRConnection(REDIS_DSN__SETTINGS, NAME, 0)
info_rconn: InfoSettingsRConnection = InfoSettingsRConnection(REDIS_DSN__INFO, NAME, CHAIN)
path_rconn: PathRConnection = PathRConnection(REDIS_DSN__PATH)
price_rconn: PriceRConnection = PriceRConnection(REDIS_DSN__PRICE)
sync_rconn: SyncRConnection = SyncRConnection(REDIS_DSN__SYNC)
price_sender: RMQConnection = RMQConnection(RMQ_HOST, RMQ_USER, RMQ_PASSWORD)

web3_conn = web3.Web3(web3.HTTPProvider(JSON_RPC_PROVIDER))


def parse_path_price(
        token0: TokenRow,
        token1: TokenRow,
        is_buy: bool,
        path: PathRow
) -> Decimal:
    fee: int
    from_: TokenRow
    to_: TokenRow
    quoter = web3_conn.eth.contract(UNI_V3_QUOTER_ADDRESS, abi=uni_v3_quoter_abi)
    amount: int = 0
    total: int = 0
    total_token = 0
    for percent, perc_path in path.chains.items():
        if is_buy:
            for path_chain in perc_path:
                from_ = path_chain.token_from
                to_ = path_chain.token_to
                if amount == 0:
                    amount = int(percent) * int(from_.decimals)
                    total += amount
                p = quoter.functions.quoteExactInputSingle(
                    (from_.address, to_.address, amount, path_chain.fee, 0)).call()
                amount = p[0]
        else:
            for path_chain in reversed(perc_path):
                from_ = path_chain.token_from
                to_ = path_chain.token_to
                if amount == 0:
                    amount = int(percent) * int(to_.decimals)
                    total += amount
                p = quoter.functions.quoteExactOutputSingle(
                    (from_.address, to_.address, amount, path_chain.fee, 0)).call()
                amount = p[0]

        total_token += amount
        amount = 0
    if is_buy:
        price = (total / token0.decimals) / (total_token / token1.decimals)
    else:
        price = (total / token1.decimals) / (total_token / token0.decimals)
    return price


def _calc_price_data(pair_symbol: str, type_: str):
    sync_key = _key.render(pair=pair_symbol, type=type_)

    if not sync_rconn.is_lock(sync_key):
        path = path_rconn.get_exchange_pair_path(NAME, pair_symbol, type_)
        if path is None: return
        actual_price = price_rconn.get_exchange_pair_price(NAME, pair_symbol)
        is_buy = type == "exactIn"
        sync_rconn.lock_action(sync_key, 60 * 2)
        pair_row = info_rconn.get_pair_info(pair_symbol)

        token0 = info_rconn.get_token_info_by_address(pair_row.token0)
        token1 = info_rconn.get_token_info_by_address(pair_row.token1)
        price = parse_path_price(token1, token0, is_buy, path) if is_buy else parse_path_price(token0, token1, is_buy, path)
        if actual_price is None:
            actual_price = PriceRow(
                price=[Decimal(0), Decimal(0)]
            )
        actual_price[is_buy] = price

        calc_entity = CalculationPrice(
            group=0,
            symbol=pair_symbol,
            exchange=NAME,
            price=actual_price,
            buy=is_buy
        )

        price_rconn.set_exchange_pair_price(NAME, pair_symbol, actual_price)
        price_sender.send_message(RABBITMQ_QUE__SENDER, calc_entity.to_bytes())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    while True:
        for pair_symbol in setting_rconn.get_pairs():
            _calc_price_data(pair_symbol, "exactIn")
            _calc_price_data(pair_symbol, "exactOut")
        time.sleep(setting_rconn.get_setting().delay)

