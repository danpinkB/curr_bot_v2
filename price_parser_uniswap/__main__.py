import asyncio
import logging
import time
from decimal import Decimal
from typing import Final, Coroutine, Any, Callable, Optional

import web3

from abstract.const import INSTRUMENTS_CONNECTIVITY, INSTRUMENTS
from abstract.exchange import Exchange
from abstract.instrument import ExchangeInstrument, Instrument, DEXExchangeInstrumentParams
from abstract.path_chain import RouteChain, QuoteType, InstrumentRoute, UniPool
from inmemory_storage.path_db.path_db import path_db
from inmemory_storage.sync_db.sync_db import sync_db
from message_broker.message_broker import message_broker
from message_broker.topics.price import publish_price_topic, LastPriceMessage, InstrumentPrice
from net_node.contracts.uniswap.v2.abi import ROUTER_ABI
from net_node.contracts.uniswap.v2.deployments import ROUTER_ADDRESS
from net_node.contracts.uniswap.v3.abi import QUOTER_V2_ABI
from net_node.contracts.uniswap.v3.deployments import QUOTER_V2_ADDRESS
from price_parser_uniswap.env import JSON_RPC_PROVIDER
from uniswap import Uniswap

NAME = "UNIv3"


REQUIRED_INSTRUMENTS = tuple(k for k, v in INSTRUMENTS_CONNECTIVITY.items() if any(ei.exchange == Exchange.UNISWAP for ei in v))
i: Instrument
p: DEXExchangeInstrumentParams
INSTRUMENT_PARAMS: Final = {i: INSTRUMENTS[ExchangeInstrument(Exchange.UNISWAP, i)].dex for i in REQUIRED_INSTRUMENTS}
INSTRUMENT_ADDRESS_PARAMS = {}

for i, p in INSTRUMENT_PARAMS.items():
    INSTRUMENT_ADDRESS_PARAMS[p.quote.address] = p.quote
    INSTRUMENT_ADDRESS_PARAMS[p.base.address] = p.base

web3_conn = web3.AsyncWeb3(web3.AsyncHTTPProvider(JSON_RPC_PROVIDER))
uniswap_v3_sdk = Uniswap(None, None, provider=JSON_RPC_PROVIDER, version=3)
uniswap_v2_sdk = Uniswap(None, None, provider=JSON_RPC_PROVIDER, version=2)

quoter = web3_conn.eth.contract(QUOTER_V2_ADDRESS, abi=QUOTER_V2_ABI)
router = web3_conn.eth.contract(ROUTER_ADDRESS, abi=ROUTER_ABI)


async def quote_in_v3(amount: int, pool: UniPool) -> int:
    res = uniswap_v3_sdk.get_price_input(pool.token_from, pool.token_to, amount, pool.fee)
    # logging.info(f'{pool} {res}')
    return res


async def quote_out_v3(amount: int, pool: UniPool) -> int:
    # logging.info(pool)
    # logging.info(f'{pool.address} {(pool.token_from, pool.token_to, amount, pool.fee, 0)}')
    res = uniswap_v3_sdk.get_price_output(pool.token_from, pool.token_to, amount, pool.fee)
    # logging.info(f'{res}')
    # logging.info(res)
    return res


async def quote_in_v2(amount: int, pool: UniPool) -> int:
    # res = await router.functions.getAmountsOut(amount, [pool.token_from, pool.token_to]).call()
    # logging.info(f'{pool} {res}')
    return uniswap_v2_sdk.get_price_input(pool.token_from, pool.token_to, amount)


async def quote_out_v2(amount: int, pool: UniPool) -> int:
    # logging.info(pool)
    # res = await router.functions.getAmountsIn(amount, [pool.token_from, pool.token_to]).call()
    # logging.info(res)
    return uniswap_v2_sdk.get_price_output(pool.token_from, pool.token_to, amount)


version_typed_executors = {
    (QuoteType.exactIn, "V3"): quote_in_v3,
    (QuoteType.exactOut, "V3"): quote_out_v3,
    (QuoteType.exactIn, "V2"): quote_in_v2,
    (QuoteType.exactOut, "V2"): quote_out_v2,
}


async def parse_route_price(
    route: InstrumentRoute
) -> Optional[Decimal]:
    path: RouteChain
    amount: int
    total: int = 0
    total_token: int = 0
    executor: Callable[[int, UniPool], Coroutine[Any, Any, int]]
    from_dec = INSTRUMENT_ADDRESS_PARAMS[route.pathes[0].pools[0].token_from].decimals
    to_dec = INSTRUMENT_ADDRESS_PARAMS[route.pathes[0].pools[len(route.pathes[0].pools) - 1].token_to].decimals
    from_dec, to_dec = (from_dec, to_dec) if route.qtype is QuoteType.exactIn else (to_dec, from_dec)
    try:
        for path in route.pathes:
            # logging.info(path)
            amount = path.amount * from_dec
            total += amount
            executor = version_typed_executors[(route.qtype, path.version)]
            for pool in path.pools if route.qtype is QuoteType.exactIn else reversed(path.pools):
                amount = await executor(amount, pool)
            total_token += amount
    except Exception as ex:
        logging.info(ex)
        return None
    return (total/from_dec)/(total_token/to_dec)


async def main():
    curr_block = 0
    path_db_ins: Final = path_db()
    locker_db: Final = sync_db()
    broker = await message_broker()
    while True:
        if curr_block == await web3_conn.eth.block_number:
            time.sleep(0.5)
            continue
        logging.info(f"block {curr_block}")
        curr_block = await web3_conn.eth.block_number
        for instrument, params in INSTRUMENT_PARAMS.items():
            if await locker_db.is_lock(instrument.value):
                continue
            quote_in_route = await path_db_ins.get_route(instrument, QuoteType.exactIn)
            quote_out_route = await path_db_ins.get_route(instrument, QuoteType.exactOut)
            if quote_in_route and quote_out_route:
                await locker_db.lock_action(instrument.value, 1000)
                # logging.info(f'{quote_in_route} \n {quote_out_route} \n')
                buy = await parse_route_price(quote_in_route)
                sell = await parse_route_price(quote_out_route)
                logging.info(f'quote_in_route {instrument.name} { buy }')
                logging.info(f'quote_out_route {instrument.name} { sell }')
                if buy and sell:
                    await publish_price_topic(
                        broker,
                        LastPriceMessage(
                            price=InstrumentPrice(
                                buy=Decimal(buy),
                                sell=Decimal(sell),
                                buy_fee=Decimal('0.1'),
                                sell_fee=Decimal('0.1')
                            ),
                            exchange=Exchange.UNISWAP,
                            instrument=instrument
                        )
                    )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
