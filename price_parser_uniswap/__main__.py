import asyncio
import json
import logging
import subprocess
import traceback
from decimal import Decimal
from typing import Optional, Dict, List, Final

import web3
from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address
from jinja2 import Template
from web3 import AsyncWeb3
from abstract.const import INSTRUMENTS_CONNECTIVITY, INSTRUMENTS, EthTokens
from abstract.exchange import Exchange
from abstract.instrument import ExchangeInstrument, Instrument, DEXExchangeInstrumentParams
from abstract.path_chain import PathChain, QuoteType, InstrumentRoute
from inmemory_storage.path_db.path_db import path_db
from inmemory_storage.sync_db.sync_db import sync_db
from inmemory_storage.tg_settings_db.tg_settings_db import tg_settings_db
from net_node.contracts.uniswap.v2.abi import ROUTER_ABI
from net_node.contracts.uniswap.v2.deployments import ROUTER_ADDRESS
from net_node.contracts.uniswap.v3.abi import QUOTER_ABI
from net_node.contracts.uniswap.v3.deployments import QUOTER_ADDRESS
from price_parser_uniswap.const import CHAIN
from price_parser_uniswap.env import JSON_RPC_PROVIDER

NAME = "UNIv3"


REQUIRED_INSTRUMENTS = tuple(k for k, v in INSTRUMENTS_CONNECTIVITY.items() if any(ei.exchange == Exchange.UNISWAP for ei in v))
INSTRUMENT_PARAMS = {i: INSTRUMENTS[ExchangeInstrument(Exchange.UNISWAP, i)].dex for i in REQUIRED_INSTRUMENTS}

web3_conn = web3.AsyncWeb3(web3.AsyncHTTPProvider(JSON_RPC_PROVIDER))
quoter = web3_conn.eth.contract(QUOTER_ADDRESS, abi=QUOTER_ABI)
router = web3_conn.eth.contract(ROUTER_ADDRESS, abi=ROUTER_ABI)


async def quote_in_v3(path: PathChain, dec_from: Decimal, dec_to: Decimal) -> Decimal:
    amount: Decimal = path.amount*dec_from
    for pool in path.pools:
        await quoter.functions.quoteExactInputSingle((pool.token_from, pool.token_to, amount, pool.fee, 0)).call()


async def quote_out_v3(path:PathChain, dec_from:Decimal, dec_to:Decimal) -> Decimal:
    amount: Decimal = Decimal(path.amount)*dec_from
    for pool in reversed(path.pools):
        amount = (await quoter.functions.quoteExactOutputSingle((pool.token_from, pool.token_to, amount, pool.fee, 0)).call())[0]
    return amount


version_typed_executors = {
    (QuoteType.exactIn, "V3"): quote_in_v3,
    (QuoteType.exactOut, "V3"): quote_out_v3,
}

async def parse_route_price(
    route: InstrumentRoute
) -> Decimal:
    path: PathChain
    amount: Decimal
    total: Decimal = Decimal(0)
    total_token = Decimal(0)
    print(route)
    params: DEXExchangeInstrumentParams
    for path in route.pathes:
        print(path.amount)
        print(path.version)
        params = INSTRUMENT_PARAMS[route.instrument]
        version_typed_executors[(route.qtype, path.version)](path, params)
        route.qtype
        if is_buy:
            for path_chain in perc_path:
                from_ = path_chain.token_from
                to_ = path_chain.token_to
                if amount == 0:
                    amount = int(percent) * int(from_.value.decimals)
                    total += amount
                p = await quoter.functions.quoteExactInputSingle(
                    (from_.value.address, to_.value.address, amount, path_chain.fee, 0)).call()
                amount = p[0]
        else:
            for path_chain in reversed(perc_path):
                from_ = path_chain.token_from
                to_ = path_chain.token_to
                if amount == 0:
                    amount = int(percent) * int(to_.value.decimals)
                    total += amount
                p = await quoter.functions.quoteExactOutputSingle(
                    (from_.value.address, to_.value.address, amount, path_chain.fee, 0)).call()
                amount = p[0]

        total_token += amount
        amount = 0
    # if is_buy:
    #     price = (total / token0.decimals) / (total_token / token1.decimals)
    # else:
    #     price = (total / token1.decimals) / (total_token / token0.decimals)
    return 0


async def main():
    path_db_ins: Final = path_db()
    locker_db: Final = sync_db()
    while True:
        for instrument, params in INSTRUMENT_PARAMS.items():
            if await locker_db.is_lock(instrument.value):
                continue
            quote_in = await path_db_ins.get_route(instrument, QuoteType.exactIn)
            quote_out = await path_db_ins.get_route(instrument, QuoteType.exactOut)
            if quote_in and quote_out:
                await locker_db.lock_action(instrument.value, 1000)
                await parse_route_price(quote_in)
                await parse_route_price(quote_out)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
