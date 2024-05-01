import asyncio
import logging
import time
from decimal import Decimal
from typing import Final, Coroutine, Any, Callable, Optional, List

import web3
from web3.exceptions import ContractLogicError

from abstract.const import INSTRUMENTS_CONNECTIVITY, INSTRUMENTS, EthTokens
from abstract.exchange import Exchange
from abstract.instrument import ExchangeInstrument, Instrument, DEXExchangeInstrumentParams
from inmemory_storage.sync_db.sync_db import sync_db
from inmemory_storage.tg_settings_db.tg_settings_db import tg_settings_db
from message_broker.message_broker import message_broker
from message_broker.topics.price import publish_price_topic, LastPriceMessage, InstrumentPrice
from net_node.contracts.uniswap.v2.abi import FACTORY_ABI, ROUTER_ABI
from net_node.contracts.uniswap.v2.deployments import FACTORY_ADDRESS, ROUTER_ADDRESS
from price_parser_uniswap_v2.env import JSON_RPC_PROVIDER


REQUIRED_INSTRUMENTS = tuple(k for k, v in INSTRUMENTS_CONNECTIVITY.items() if any(ei.exchange == Exchange.UNISWAP for ei in v))
i: Instrument
p: DEXExchangeInstrumentParams


async def main():
    curr_block = 0
    web3_conn = web3.AsyncWeb3(web3.AsyncHTTPProvider(JSON_RPC_PROVIDER))

    settings_db: Final = tg_settings_db()
    locker_db: Final = sync_db()
    broker = await message_broker()

    factory = web3_conn.eth.contract(FACTORY_ADDRESS, abi=FACTORY_ABI)
    router = web3_conn.eth.contract(ROUTER_ADDRESS, abi=ROUTER_ABI)

    INSTRUMENT_PARAMS = {}
    INSTRUMENT_ADDRESS_PARAMS = {}

    for i in REQUIRED_INSTRUMENTS:
        p = INSTRUMENTS[ExchangeInstrument(Exchange.UNISWAP, i)].dex
        if p.base.address == EthTokens.ETH.value.address:
            INSTRUMENT_PARAMS[i] = p
            continue
        address = await factory.functions.getPair(p.base.address, EthTokens.ETH.value.address).call()
        if address != '0x0000000000000000000000000000000000000000':
            INSTRUMENT_PARAMS[i] = p

    for i, p in INSTRUMENT_PARAMS.items():
        INSTRUMENT_ADDRESS_PARAMS[p.quote.address] = p.quote
        INSTRUMENT_ADDRESS_PARAMS[p.base.address] = p.base

    while True:
        if curr_block == await web3_conn.eth.block_number:
            time.sleep(0.5)
            continue
        settings = await settings_db.get_settings()
        logging.info(f"block {curr_block}")
        curr_block = await web3_conn.eth.block_number
        params: DEXExchangeInstrumentParams
        route: List[str]
        dec0: Decimal
        dec1: Decimal

        def _calc_uni_price(call_result: List[int], is_buy: bool):
            last_index = len(call_result) - 1
            l, r = (Decimal(call_result[0]), Decimal(call_result[last_index])) if is_buy else (Decimal(call_result[last_index]), Decimal(call_result[0]))
            return (l / dec0) / (r / dec1)

        for instrument, params in INSTRUMENT_PARAMS.items():
            dec0 = Decimal(params.quote.decimals)
            dec1 = Decimal(params.base.decimals)
            if await locker_db.is_lock(instrument.value):
                continue
            # logging.info(f"quoting instrument {instrument.name}")
            calc_volume = settings.calc_volume*params.quote.decimals
            try:
                route = [params.base.address, params.quote.address] if params.base.address == EthTokens.ETH.value.address else [params.base.address, EthTokens.ETH.value.address, params.quote.address]
                sell_price = _calc_uni_price(await router.functions.getAmountsIn(calc_volume, route).call(), False)
                route.reverse()
                buy_price = _calc_uni_price(await router.functions.getAmountsOut(calc_volume, route).call(), True)
                # logging.info(f'{instrument.name} buy {buy_price} sell {sell_price}')
                # logging.info(f'quote_in_route {instrument.name} { buy[1] / params.base.decimals}')
                # logging.info(f'quote_out_route {instrument.name} { sell[0] / params.base.decimals }')

                await publish_price_topic(
                    broker,
                    LastPriceMessage(
                        price=InstrumentPrice(
                            buy=Decimal(buy_price),
                            sell=Decimal(sell_price),
                            buy_fee=Decimal('0.1'),
                            sell_fee=Decimal('0.1')
                        ),
                        exchange=Exchange.UNISWAP,
                        instrument=instrument
                    )
                )

            except ContractLogicError:
                logging.error(f'instrument invalid {instrument.name}')
                continue


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
