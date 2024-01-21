import json
import logging
import subprocess
import traceback
from decimal import Decimal
from typing import Optional, Dict, List, Final

from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address
from jinja2 import Template
from web3 import AsyncWeb3
from abstract.const import INSTRUMENTS_CONNECTIVITY, INSTRUMENTS, EthTokens
from abstract.exchange import Exchange
from abstract.instrument import ExchangeInstrument, Instrument
from abstract.path_chain import PathChain
from inmemory_storage.kv_db import kv_db
from inmemory_storage.sync_db.sync_db import sync_db
from inmemory_storage.tg_settings_db.tg_settings_db import tg_settings_db
from net_node.contracts.uniswap.v2.abi import ROUTER_ABI
from net_node.contracts.uniswap.v2.deployments import ROUTER_ADDRESS
from net_node.contracts.uniswap.v3.abi import QUOTER_ABI
from net_node.contracts.uniswap.v3.deployments import QUOTER_ADDRESS
from price_parser_uniswap.const import CHAIN
from price_parser_uniswap.env import UNI_CLI_PATH

NAME = "UNIv3"

setting_db: Final = tg_settings_db()
path_db: Final = kv_db()
sync_db: Final = sync_db()

REQUIRED_INSTRUMENTS = tuple(k for k, v in INSTRUMENTS_CONNECTIVITY.items() if any(ei.exchange == Exchange.UNISWAP for ei in v))
INSTRUMENT_ARGUMENTS = {INSTRUMENTS[ExchangeInstrument(Exchange.UNISWAP, i)].dex: i for i in REQUIRED_INSTRUMENTS}


def parse_path_price(
        token0: str,
        token1: str,
        is_buy: bool,
        path: PathChain,
        web3_conn: AsyncWeb3
) -> Decimal:
    fee: int
    from_: EthTokens
    to_: EthTokens
    quoter = web3_conn.eth.contract(QUOTER_ADDRESS, abi=QUOTER_ABI)
    router = web3_conn.eth.contract(ROUTER_ADDRESS, abi=ROUTER_ABI)
    amount: int = 0
    total: int = 0
    total_token = 0
    for percent, perc_path in path.chains.items():
        if is_buy:
            for path_chain in perc_path:
                from_ = path_chain.token_from
                to_ = path_chain.token_to
                if amount == 0:
                    amount = int(percent) * int(from_.value.decimals)
                    total += amount
                p = quoter.functions.quoteExactInputSingle(
                    (from_.value.address, to_.value.address, amount, path_chain.fee, 0)).call()
                amount = p[0]
        else:
            for path_chain in reversed(perc_path):
                from_ = path_chain.token_from
                to_ = path_chain.token_to
                if amount == 0:
                    amount = int(percent) * int(to_.value.decimals)
                    total += amount
                p = quoter.functions.quoteExactOutputSingle(
                    (from_.value.address, to_.value.address, amount, path_chain.fee, 0)).call()
                amount = p[0]

        total_token += amount
        amount = 0
    if is_buy:
        price = (total / token0.decimals) / (total_token / token1.decimals)
    else:
        price = (total / token1.decimals) / (total_token / token0.decimals)
    return price


def _parse_path_info(instrument: Instrument, type_: str) -> Optional[PathRow]:
    path = path_db.get(f'{instrument.value}{type_}')
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
