import json
import logging
import subprocess
import traceback
from typing import Optional, Dict, List

import web3
from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address
from jinja2 import Template

from obs_shared.connection.active_settings_exchange_rconn import ActiveSettingsExchangeRConnection
from obs_shared.connection.info_db_rconn import InfoSettingsRConnection
from obs_shared.connection.path_db_rconn import PathRConnection
from obs_shared.connection.sync_db_rconn import SyncRConnection
from obs_shared.types.path_row import PathRow, PathRowChain
from obs_shared.types.token_row import TokenRow
from obs_shared.utils.erc20_token_utils import get_token_info_from_json
from path_parser_uniswap.const import CHAIN
from path_parser_uniswap.env import REDIS_DSN__INFO, REDIS_DSN__PATH, REDIS_DSN__SYNC, JSON_RPC_PROVIDER, UNI_CLI_PATH, \
    REDIS_DSN__SETTINGS

NAME = "UNIv3"

setting_rconn: ActiveSettingsExchangeRConnection = ActiveSettingsExchangeRConnection(REDIS_DSN__SETTINGS, NAME, 0)
info_rconn: InfoSettingsRConnection = InfoSettingsRConnection(REDIS_DSN__INFO, NAME, CHAIN)
path_rconn: PathRConnection = PathRConnection(REDIS_DSN__PATH)
sync_rconn: SyncRConnection = SyncRConnection(REDIS_DSN__SYNC)

web3_connection = web3.Web3(web3.HTTPProvider(JSON_RPC_PROVIDER))
path_key = Template("{{pair}}_path_{{type}}")


def _quote(symbol: str, token0: ChecksumAddress, token1: ChecksumAddress, amount: int, type_: str, protocols: str) -> Optional[PathRow]:
    command = f'{UNI_CLI_PATH}bin/cli quote-custom --tokenIn {token0} --tokenOut {token1} --amount {amount} --{type_} --recipient 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B --protocols {protocols}'
    cli_result = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
    logging.info(f"{command}\n{cli_result}")
    try:
        output = cli_result[0].decode("utf-8").replace("\n", "")
        if "Could not find route" in output:
            return None
        raw_pair_path = json.loads(output.strip())
        token0_path_chain: TokenRow
        token1_path_chain: TokenRow
        from_token: ChecksumAddress
        chains: Dict[str, List[PathRowChain]] = dict()
        chain_list: List[PathRowChain]
        for amount, raw_pair_pathes in raw_pair_path.items():
            chain_list = list()
            for raw_pair_path in raw_pair_pathes:
                from_token = to_checksum_address(raw_pair_path.get("from_token"))
                token0_path_chain = get_token_info_from_json(raw_pair_path.get("token0"), CHAIN)
                token1_path_chain = get_token_info_from_json(raw_pair_path.get("token1"), CHAIN)
                token0_path_chain, token1_path_chain = (token1_path_chain, token0_path_chain) if from_token == token1_path_chain.address else (token0_path_chain, token1_path_chain)

                chain_list.append(PathRowChain(
                    token_from=token0_path_chain,
                    token_to=token1_path_chain,
                    fee=raw_pair_path.get("fee")
                ))
            chains[amount] = chain_list
        return PathRow(chains=chains)
    except Exception:
        logging.error(traceback.format_exc())
        return None


def _parse_path_info(pair_symbol: str, type_: str) -> Optional[PathRow]:
    pair_row = info_rconn.get_pair_info(pair_symbol)
    return _quote(pair_symbol, pair_row.token0, pair_row.token1, setting_rconn.get_setting().rvolume, type_, "v3")


def _parse_path(pair_symbol: str, type_: str):
    sync_key = path_key.render(pair=pair_symbol, type=type_)
    if not sync_rconn.is_lock(sync_key):
        sync_rconn.lock_action(sync_key, 60 * 2)
        path = _parse_path_info(pair_symbol, type_)
        # if path is None:
        #     setting_rconn.deactivate_ex_pair(NAME, pair_symbol)
        # else:
        if path is not None:
            path_rconn.set_exchange_pair_path(NAME, pair_symbol, path, type_)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    while True:
        for pair_symbol in setting_rconn.get_pairs():
            _parse_path(pair_symbol, "exactIn")
            _parse_path(pair_symbol, "exactOut")
