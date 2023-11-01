import asyncio
import logging
import re
import shlex
import subprocess
import traceback
from _decimal import Decimal
from typing import Optional, NamedTuple, Callable, Any

import web3
from eth_typing import ChecksumAddress
from jinja2 import Template

from abstract.const import INSTRUMENTS_CONNECTIVITY, INSTRUMENTS
from abstract.exchange import Exchange
from abstract.instrument import ExchangeInstrument, DEXExchangeInstrumentParams, Instrument
from kv_db.db_price_parser_uniswap_sync.db_price_parser_uniswap_sync import db_price_parser_uniswap_sync
from message_broker.message_broker import message_broker
from message_broker.topics.price import LastPriceMessage, InstrumentPrice, publish_price_topic
from price_parser_uniswap.env import JSON_RPC_PROVIDER, UNI_CLI_PATH

NAME = "UNIv3"

web3_connection = web3.Web3(web3.HTTPProvider(JSON_RPC_PROVIDER))
path_key = Template("{{pair}}_path_{{type}}")

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|[ \t\n"]')

REQUIRED_INSTRUMENTS = tuple(k for k, v in INSTRUMENTS_CONNECTIVITY.items() if any(ei.exchange == Exchange.UNISWAP for ei in v))
INSTRUMENT_ARGUMENTS = {INSTRUMENTS[ExchangeInstrument(Exchange.UNISWAP, i)].dex: i for i in REQUIRED_INSTRUMENTS}


class FieldMapper(NamedTuple):
    field_name: str
    apply: Callable[[Any], Any]


class CLIQuoteUniswap(NamedTuple):
    best_route: str
    amount: Decimal
    quote_in: Decimal
    gas_quote: Decimal
    gas_usd: Decimal
    call_data: str
    block_number: int


mapper = {
    1: FieldMapper(
        field_name="best_route",
        apply=lambda x: x
    ),
    5: FieldMapper(
        field_name="quote_in",
        apply=lambda x: Decimal(x)
    ),
    7: FieldMapper(
        field_name="gas_quote",
        apply=lambda x: Decimal(x[18:])
    ),
    8: FieldMapper(
        field_name="gas_usd",
        apply=lambda x: Decimal(x[11:])
    ),
    9: FieldMapper(
        field_name="call_data",
        apply=lambda x: x[9:]
    ),
    12: FieldMapper(
        field_name="block_number",
        apply=lambda x: x[12:]
    )
}
CLI_HEIGHT = range(13)


async def _quote(base: ChecksumAddress, quote: ChecksumAddress, amount: Decimal, type_: str) -> Optional[CLIQuoteUniswap]:
    command = f'{UNI_CLI_PATH}/bin/cli quote -i {quote} -o {base} --amount {amount} --{type_} --recipient 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B --protocols v3'
    args = shlex.split(command)
    process = await asyncio.create_subprocess_exec(*args, cwd=UNI_CLI_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    quote = {}
    field_mapper: Optional[FieldMapper]

    for line_number in CLI_HEIGHT:
        field_mapper = mapper.get(line_number)
        line = await process.stdout.readline()
        if field_mapper is not None:
            quote[field_mapper.field_name] = field_mapper.apply(ansi_escape.sub('', line.decode("utf-8")))
    if len(quote) > 0:
        return CLIQuoteUniswap(amount=amount, **quote)


async def main():
    curr_block_number = 0
    broker = await message_broker()
    sync_manager = db_price_parser_uniswap_sync()
    amount = Decimal(10000)

    while True:
        if curr_block_number != connection.eth.block_number:
            p: DEXExchangeInstrumentParams
            i: Instrument

            for p, i in INSTRUMENT_ARGUMENTS.items():
                if sync_manager.is_unlocked(i, 12000):
                    logging.info(i.name)
                    try:
                        buy = await _quote(p.base.address, p.quote.address, amount, "exactIn")
                        sell = await _quote(p.quote.address, p.base.address, amount, "exactOut")

                        last_price = LastPriceMessage(
                            price=InstrumentPrice(buy=amount / buy.quote_in, sell=amount / sell.quote_in, buy_fee=buy.gas_usd, sell_fee=sell.gas_usd),
                            exchange=Exchange.UNISWAP,
                            instrument=i
                        )
                        logging.info(last_price)
                        await publish_price_topic(broker, last_price)
                    except Exception as ex:
                        traceback.print_exc()
                        logging.error(ex)
                        logging.info(i.name)

            curr_block_number = connection.eth.block_number


if __name__ == '__main__':
    connection = web3.Web3(web3.HTTPProvider(JSON_RPC_PROVIDER))
    from abstract.logger_wrapper import wrap_logger
    wrap_logger()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
