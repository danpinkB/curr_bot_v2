import json
import time
from _decimal import Decimal
from typing import Optional, Tuple

import web3
from jinja2 import Template
from obs_shared.connection import PathRConnection, SyncRConnection, RMQConnection, ActiveSettingsRConnection, InfoSettingsRConnection
from obs_shared.static import uni_v3_quoter_abi
from obs_shared.types import CalculationPrice, TokenRow

from src.const import PATH_R_HOST, PATH_R_DB, PATH_R_PASSWORD, SYNC_R_HOST, SYNC_R_DB, SYNC_R_PASSWORD, SENDER_RMQ_QUE, \
    SENDER_RMQ_PASSWORD, SENDER_RMQ_USER, SENDER_RMQ_HOST, SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD, \
    INFO_R_HOST, INFO_R_DB, INFO_R_PASSWORD, JSON_RPC_PROVIDER, UNI_V3_QUOTER_ADDRESS, CHAIN

NAME = "UNIv3"
_key = Template("{{pair}}_price_{{type}}")

setting_rconn: ActiveSettingsRConnection = ActiveSettingsRConnection(SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD, NAME, 0)
info_rconn: InfoSettingsRConnection = InfoSettingsRConnection(INFO_R_HOST, INFO_R_DB, INFO_R_PASSWORD, NAME, CHAIN)
path_rconn: PathRConnection = PathRConnection(PATH_R_HOST, PATH_R_DB, PATH_R_PASSWORD)
sync_rconn: SyncRConnection = SyncRConnection(SYNC_R_HOST, SYNC_R_DB, SYNC_R_PASSWORD)
price_sender: RMQConnection = RMQConnection(SENDER_RMQ_HOST, SENDER_RMQ_USER, SENDER_RMQ_PASSWORD)

web3_conn = web3.Web3(web3.HTTPProvider(JSON_RPC_PROVIDER))


def parse_path_price(
        token0: TokenRow,
        token1: TokenRow,
        is_buy: bool,
        path: dict
) -> Decimal:
    fee: int
    token0_path_chain: Tuple[str, str, str, str, int]
    token1_path_chain: Tuple[str, str, str, str, int]
    quoter = web3_conn.eth.contract(UNI_V3_QUOTER_ADDRESS, abi=uni_v3_quoter_abi)
    amount: int = 0
    total: int = 0
    total_token = 0
    for percent, perc_path in path.items():
        if is_buy:
            for path_chain in perc_path:
                token0_path_chain = path_chain.get("token0")
                token1_path_chain = path_chain.get("token1")
                fee = path_chain.get("fee")
                if amount == 0:
                    amount = int(percent) * int(token0_path_chain[3])
                    total += amount
                p = quoter.functions.quoteExactInputSingle(
                    (token0_path_chain[0], token1_path_chain[0], amount, fee, 0)).call()
                amount = p[0]
        else:
            for path_chain in reversed(perc_path):
                token0_path_chain = path_chain.get("token0")
                token1_path_chain = path_chain.get("token1")
                fee = path_chain.get("fee")
                if amount == 0:
                    amount = int(percent) * int(token1_path_chain[3])
                    total += amount
                p = quoter.functions.quoteExactOutputSingle(
                    (token0_path_chain[0], token1_path_chain[0], amount, fee, 0)).call()
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
        is_buy = type == "exactIn"
        sync_rconn.lock_action(sync_key, 60 * 2)
        pair_row = info_rconn.get_pair_info(pair_symbol)
        path = json.loads(path_rconn.get_exchange_pair_path(NAME, pair_symbol, type_))
        if path is None:
            return None
        token0 = info_rconn.get_token_info_by_address(pair_row.token0)
        token1 = info_rconn.get_token_info_by_address(pair_row.token1)
        price = parse_path_price(token0, token1, is_buy, path)
        calc_entity = CalculationPrice(
            group=0,
            symbol=pair_symbol,
            exchange=NAME,
            price=price,
            buy=is_buy
        )
        price_sender.send_message(SENDER_RMQ_QUE, calc_entity.to_bytes())


if __name__ == '__main__':
    while True:
        for pair_symbol in setting_rconn.get_pairs():
            _calc_price_data(pair_symbol, "exactIn")
            _calc_price_data(pair_symbol, "exactOut")
        time.sleep(setting_rconn.get_setting().delay)

