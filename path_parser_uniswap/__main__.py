import json
import logging
import subprocess
import traceback
from typing import Optional, Dict, List, Final

from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address
from jinja2 import Template

from abstract.const import INSTRUMENTS_CONNECTIVITY, INSTRUMENTS
from abstract.exchange import Exchange
from abstract.instrument import ExchangeInstrument, Instrument
from inmemory_storage.kv_db import kv_db
from inmemory_storage.sync_db.sync_db import sync_db
from inmemory_storage.tg_settings_db.tg_settings_db import tg_settings_db
from path_parser_uniswap.const import CHAIN
from path_parser_uniswap.env import UNI_CLI_PATH

NAME = "UNIv3"

setting_db: Final = tg_settings_db()
path_db: Final = kv_db()
sync_db: Final = sync_db()

REQUIRED_INSTRUMENTS = tuple(k for k, v in INSTRUMENTS_CONNECTIVITY.items() if any(ei.exchange == Exchange.UNISWAP for ei in v))
INSTRUMENT_ARGUMENTS = {INSTRUMENTS[ExchangeInstrument(Exchange.UNISWAP, i)].dex:i for i in REQUIRED_INSTRUMENTS}

path_key = Template("{{pair}}_path_{{type}}")


def _quote(symbol: str, from_token: ChecksumAddress, to_token: ChecksumAddress, amount: int, type_: str, protocols: str) -> Optional[PathRow]:
    command = f'{UNI_CLI_PATH}bin/cli quote-custom --tokenIn {from_token} --tokenOut {to_token} --amount {amount} --{type_} --recipient 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B --protocols {protocols}'
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


def _parse_path_info(instrument: Instrument, type_: str) -> Optional[PathRow]:
    instrument.name
    pair_row = info_rconn.get_pair_info(pair_symbol)
    if type_ == "exactIn":
        return _quote(pair_symbol, pair_row.token1, pair_row.token0, setting_db.get_setting().rvolume, type_, "v3")
    return _quote(pair_symbol, pair_row.token0, pair_row.token1, setting_db.get_setting().rvolume, type_, "v3")


def _parse_path(pair_symbol: str, type_: str):
    sync_key = path_key.render(pair=pair_symbol, type=type_)
    if not sync_db.is_lock(sync_key):
        sync_db.lock_action(sync_key, 60 * 2)
        path = _parse_path_info(pair_symbol, type_)
        # if path is None:
        #     setting_rconn.deactivate_ex_pair(NAME, pair_symbol)
        # else:
        if path is not None:
            path_db.set_exchange_pair_path(NAME, pair_symbol, path, type_)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    while True:
        for instrument in REQUIRED_INSTRUMENTS:
            _parse_path(instrument, "exactIn")
            _parse_path(instrument, "exactOut")
