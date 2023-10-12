import json
from typing import Optional

import web3
from jinja2 import Template
from obs_shared.connection import PathRConnection, SyncRConnection, ActiveSettingsRConnection, InfoSettingsRConnection

from src.const import PATH_R_HOST, PATH_R_DB, PATH_R_PASSWORD, SYNC_R_HOST, SYNC_R_DB, SYNC_R_PASSWORD, SETTINGS_R_HOST, \
    SETTINGS_R_DB, SETTINGS_R_PASSWORD, \
    INFO_R_HOST, INFO_R_DB, INFO_R_PASSWORD, JSON_RPC_PROVIDER
from src.core import UniExchangeV3, NAME

setting_rconn: ActiveSettingsRConnection = ActiveSettingsRConnection(SETTINGS_R_HOST, SETTINGS_R_DB,
                                                                     SETTINGS_R_PASSWORD)
info_rconn: InfoSettingsRConnection = InfoSettingsRConnection(INFO_R_HOST, INFO_R_DB, INFO_R_PASSWORD)
path_rconn: PathRConnection = PathRConnection(PATH_R_HOST, PATH_R_DB, PATH_R_PASSWORD)
sync_rconn: SyncRConnection = SyncRConnection(SYNC_R_HOST, SYNC_R_DB, SYNC_R_PASSWORD)

ex = UniExchangeV3(web3.HTTPProvider(JSON_RPC_PROVIDER))

path_key = Template("{{pair}}_path_{{type}}")


def _parse_path_info(pair_symbol: str, type_: str) -> Optional[dict]:
    pair_row = info_rconn.get_pair_info(pair_symbol, 5)
    token0 = info_rconn.get_token_info_by_address(pair_row.token0, 5)
    token1 = info_rconn.get_token_info_by_address(pair_row.token1, 5)
    return ex.parse_path(pair_symbol, token0, token1, type_)


def _parse_path(pair_symbol: str, type_: str):
    sync_key = path_key.render(pair=pair_symbol, type=type_)
    if not sync_rconn.is_lock(sync_key):
        sync_rconn.lock_action(sync_key, 60 * 2)
        path = _parse_path(pair_symbol, type_)
        # if path is None:
        #     setting_rconn.deactivate_ex_pair(NAME, pair_symbol)
        # else:
        if path is not None:
            path_rconn.set_exchange_pair_path(NAME, pair_symbol, json.dumps(path), type_)


if __name__ == '__main__':
    while True:
        for pair_symbol in setting_rconn.get_ex_pairs(NAME):
            _parse_path(pair_symbol, "exactIn")
            _parse_path(pair_symbol, "exactOut")
