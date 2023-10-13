import json
import logging
import subprocess
import traceback
from typing import Optional, Dict, List, Tuple

import web3
from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address
from jinja2 import Template
from obs_shared.connection import PathRConnection, SyncRConnection, ActiveSettingsExchangeRConnection, InfoSettingsRConnection
from obs_shared.types import TokenRow
from obs_shared.utils.erc20_token_utils import get_token_info_from_json

from src.const import CHAIN
from src.env import PATH_R_HOST, PATH_R_DB, PATH_R_PASSWORD, SYNC_R_HOST, SYNC_R_DB, SYNC_R_PASSWORD, SETTINGS_R_HOST, \
    SETTINGS_R_DB, SETTINGS_R_PASSWORD, \
    INFO_R_HOST, INFO_R_DB, INFO_R_PASSWORD, JSON_RPC_PROVIDER, UNI_CLI_PATH

NAME = "UNIv3"

setting_rconn: ActiveSettingsExchangeRConnection = ActiveSettingsExchangeRConnection(SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD, NAME, 0)
info_rconn: InfoSettingsRConnection = InfoSettingsRConnection(INFO_R_HOST, INFO_R_DB, INFO_R_PASSWORD, NAME)
path_rconn: PathRConnection = PathRConnection(PATH_R_HOST, PATH_R_DB, PATH_R_PASSWORD)
sync_rconn: SyncRConnection = SyncRConnection(SYNC_R_HOST, SYNC_R_DB, SYNC_R_PASSWORD)

web3_connection = web3.Web3(web3.HTTPProvider(JSON_RPC_PROVIDER))
path_key = Template("{{pair}}_path_{{type}}")


def _quote(symbol: str, token0: ChecksumAddress, token1: ChecksumAddress, amount: int, type_: str, protocols: str) -> Optional[Dict[str, str]]:
    command = f'{UNI_CLI_PATH}bin/cli quote-custom --tokenIn {token0} --tokenOut {token1} --amount {amount} --{type_} --recipient 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B --protocols {protocols}'
    cli_result = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
    logging.info(f"{command}\n{cli_result}")
    try:
        output = cli_result[0].decode("utf-8").replace("\n", "")
        if "Could not find route" in output:
            return None
        raw_pair_path = json.loads(output.strip())
        pair_path_entity: Dict[str, List[Tuple[str, str, str, int]]] = dict()
        token0_path_chain: TokenRow
        token1_path_chain: TokenRow
        from_token: ChecksumAddress

        for amount in raw_pair_path:
            pathes =
            for raw_pair_path in raw_pair_path[amount]:

                from_token = to_checksum_address(raw_pair_path.get("from_token"))
                token0_path_chain = get_token_info_from_json(raw_pair_path.get("token0"), CHAIN)
                token1_path_chain = get_token_info_from_json(raw_pair_path.get("token1"), CHAIN)
                if from_token == token1_path_chain.address:
                    raw_pair_path['token0'] = token1_path_chain.to_string()
                    raw_pair_path['token1'] = token0_path_chain.to_string()
                else:
                    raw_pair_path['token1'] = token1_path_chain.to_string()
                    raw_pair_path['token0'] = token0_path_chain.to_string()
            pair_path_entity[amount] =
        return pool_pathes
    except Exception:
        logging.error(traceback.format_exc())
        return None


def _parse_path_info(pair_symbol: str, type_: str) -> Optional[dict]:
    pair_row = info_rconn.get_pair_info(pair_symbol)
    return _quote(pair_symbol, pair_row.token0, pair_row.token1, setting_rconn.get_settings().rvolume, type_, "v3")


def _parse_path(pair_symbol: str, type_: str):
    sync_key = path_key.render(pair=pair_symbol, type=type_)
    if not sync_rconn.is_lock(sync_key):
        sync_rconn.lock_action(sync_key, 60 * 2)
        path = _parse_path_info(pair_symbol, type_)
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
