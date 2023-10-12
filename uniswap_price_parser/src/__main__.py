import json
from _decimal import Decimal
from typing import Optional

import web3
from jinja2 import Template
from obs_shared.connection import PathRConnection, SyncRConnection, RMQConnection, ActiveSettingsRConnection, InfoSettingsRConnection
from obs_shared.types import CalculationPrice

from src.const import PATH_R_HOST, PATH_R_DB, PATH_R_PASSWORD, SYNC_R_HOST, SYNC_R_DB, SYNC_R_PASSWORD, SENDER_RMQ_QUE, \
    SENDER_RMQ_PASSWORD, SENDER_RMQ_USER, SENDER_RMQ_HOST, SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD, \
    INFO_R_HOST, INFO_R_DB, INFO_R_PASSWORD, JSON_RPC_PROVIDER, RESIDENT_SLEEPER_DELAY
from src.core import UniExchangeV3, NAME

setting_rconn: ActiveSettingsRConnection = ActiveSettingsRConnection(SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD)
info_rconn: InfoSettingsRConnection = InfoSettingsRConnection(INFO_R_HOST, INFO_R_DB, INFO_R_PASSWORD)
path_rconn: PathRConnection = PathRConnection(PATH_R_HOST, PATH_R_DB, PATH_R_PASSWORD)
sync_rconn: SyncRConnection = SyncRConnection(SYNC_R_HOST, SYNC_R_DB, SYNC_R_PASSWORD)
price_sender: RMQConnection = RMQConnection(SENDER_RMQ_HOST, SENDER_RMQ_USER, SENDER_RMQ_PASSWORD)

ex = UniExchangeV3(web3.HTTPProvider(JSON_RPC_PROVIDER))

_key = Template("{{pair}}_price_{{type}}")


def _parse_price(pair_symbol: str, is_buy: bool) -> Optional[Decimal]:
    pair_row = info_rconn.get_pair_info(pair_symbol, 5)
    path = json.loads(path_rconn.get_exchange_pair_path(NAME, pair_symbol, type_))
    if path is None:
        return None
    token0 = info_rconn.get_token_info_by_address(pair_row.token0, 5)
    token1 = info_rconn.get_token_info_by_address(pair_row.token1, 5)
    return ex.parse_price(token0, token1, is_buy, path)


def _parse_path(pair_symbol: str, type_: str):
    sync_key = _key.render(pair=pair_symbol, type=type_)
    if not sync_rconn.is_lock(sync_key):
        is_buy = type == "exactIn"
        sync_rconn.lock_action(sync_key, 60 * 2)
        price = _parse_price(pair_symbol, is_buy)
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
        for pair_symbol in setting_rconn.get_ex_pairs(NAME):
            _parse_path(pair_symbol, "exactIn")
            _parse_path(pair_symbol, "exactOut")