import asyncio
import logging
import random
import re
import shlex
import subprocess
import time
from typing import Optional, NamedTuple, Callable, Any, Final, Tuple

import web3
from eth_typing import ChecksumAddress
from jinja2 import Template

from abstract.const import INSTRUMENTS_CONNECTIVITY, INSTRUMENTS
from abstract.exchange import Exchange
from abstract.instrument import ExchangeInstrument, DEXExchangeInstrumentParams, Instrument
from abstract.path_chain import RouteChain, QuoteType, InstrumentRoute
from inmemory_storage.path_db.path_db import path_db
from inmemory_storage.sync_db.sync_db import sync_db
from inmemory_storage.tg_settings_db.tg_settings_db import tg_settings_db
from path_parser_uniswap.env import JSON_RPC_PROVIDER, UNI_CLI_PATH

NAME = "UNIv3"

ansi_escape = re.compile(r'^\s+|\s+$')

REQUIRED_INSTRUMENTS = tuple(k for k, v in INSTRUMENTS_CONNECTIVITY.items() if any(ei.exchange == Exchange.UNISWAP for ei in v))
INSTRUMENT_PARAMS = {i: INSTRUMENTS[ExchangeInstrument(Exchange.UNISWAP, i)].dex for i in REQUIRED_INSTRUMENTS}


# class FieldMapper(NamedTuple):
#     field_name: str
#     apply: Callable[[Any], Any]


# mapper = {
#     1: FieldMapper(
#         field_name="best_route",
#         apply=lambda x: x
#     ),
#     5: FieldMapper(
#         field_name="quote_in",
#         apply=lambda x: x
#     ),
#     7: FieldMapper(
#         field_name="gas_quote",
#         apply=lambda x: x[18:]
#     ),
#     8: FieldMapper(
#         field_name="gas_usd",
#         apply=lambda x: x[13:]
#     ),
#     9: FieldMapper(
#         field_name="call_data",
#         apply=lambda x: x[9:]
#     ),
#     12: FieldMapper(
#         field_name="block_number",
#         apply=lambda x: x[12:]
#     )
# }
# cli_height = range(13)

CLI_TEMPLATE: Final = Template(UNI_CLI_PATH+'bin/cli quote -i {{quote}} -o {{base}} --amount {{amount}} --{{qtype}} --recipient 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B --protocols v2,v3')


async def _quote(params: DEXExchangeInstrumentParams, amount: float, qtype: QuoteType) -> Optional[Tuple[RouteChain, ...]]:
    base, quote = (params.base.address, params.quote.address) if qtype is QuoteType.exactIn else (params.quote.address, params.base.address)
    process = await asyncio.create_subprocess_exec(
        *shlex.split(
            CLI_TEMPLATE.render(
                quote=quote,
                base=base,
                amount=amount,
                qtype=qtype.name
            )
        ),
        cwd=UNI_CLI_PATH,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # quote = {}
    line = await process.stdout.readline()
    if len(line) == 0:
        return None
    logging.info(f"quote result {line}")
    line = eval(line.decode("utf-8"))
    # for ind in cli_height:
    #     line = await process.stdout.readline()
    #     if line and mapper.get(ind):
    #         quote[mapper[ind].field_name] = mapper[ind].apply(ansi_escape.sub('', line.decode("utf-8")))
    return tuple(RouteChain.from_data(pch) for pch in line) if line else None


async def main():
    setting_db: Final = tg_settings_db()
    path_db_ins: Final = path_db()
    locker_db: Final = sync_db()
    quote_in_route: Optional[Tuple[RouteChain, ...]]
    quote_out_route: Optional[Tuple[RouteChain, ...]]
    instrument_params: DEXExchangeInstrumentParams
    i: Instrument
    while True:
        for i, instrument_params in INSTRUMENT_PARAMS.items():
            if not await locker_db.is_lock(i.value):
                logging.info(i.name)
                await locker_db.lock_action(i.value, 30000)
                quote_in_route = await _quote(
                    instrument_params,
                    amount=10000,
                    qtype=QuoteType.exactIn
                )
                quote_out_route = await _quote(
                    instrument_params,
                    amount=10000,
                    qtype=QuoteType.exactOut
                )

                if quote_in_route:
                    quote_in_route = tuple(route for route in quote_in_route)
                    await path_db_ins.set_route(
                        InstrumentRoute(
                            instrument=i,
                            qtype=QuoteType.exactIn,
                            pathes=quote_in_route
                        )
                    )
                if quote_out_route:
                    await path_db_ins.set_route(
                        InstrumentRoute(
                            instrument=i,
                            qtype=QuoteType.exactOut,
                            pathes=quote_out_route
                        )
                    )
                # await publish_price_topic(broker, LastPriceMessage(
                #     price=InstrumentPrice(buy=buy.quote_in, sell=sell.quote_in, buy_fee=buy.gas_usd, sell_fee=sell.gas_usd),
                #     exchange=Exchange.UNISWAP,
                #     instrument=i
                # ))


if __name__ == '__main__':
    time.sleep((random.random() * 10) / 5)
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
