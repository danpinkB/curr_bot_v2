import asyncio
import re
import shlex
import subprocess
import time
import traceback
from _decimal import Decimal
from datetime import datetime
from typing import Optional, NamedTuple, Callable, Any, Tuple, Dict, List

import web3
from eth_typing import ChecksumAddress
from jinja2 import Template

from abstract.logger_wrapper import wrap_logger
from abstract.const import INSTRUMENTS_CONNECTIVITY, INSTRUMENTS
from abstract.exchange import Exchange
from abstract.instrument import ExchangeInstrument, DEXExchangeInstrumentParams, Instrument
from message_broker.async_rmq_connection import RMQConnectionAsync
from message_broker.message_broker import message_broker
from message_broker.topics.price import LastPriceMessage, InstrumentPrice, publish_price_topic
from miner_geth.env import JSON_RPC_PROVIDER
from miner_price_parser_uniswap.env import UNI_CLI_PATH


logger = wrap_logger(__file__)

NAME = "UNIv3"

web3_connection = web3.Web3(web3.HTTPProvider(JSON_RPC_PROVIDER))
path_key = Template("{{pair}}_path_{{type}}")

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])|[ \t\n"]')

REQUIRED_INSTRUMENTS: Tuple[Instrument, ...] = tuple(
    k for k, v in INSTRUMENTS_CONNECTIVITY.items()
    if any(ei.exchange == Exchange.UNISWAP for ei in v)
)
INSTRUMENT_ARGUMENTS: Dict[DEXExchangeInstrumentParams, Instrument] = {
    INSTRUMENTS[ExchangeInstrument(Exchange.UNISWAP, i)].dex: i
    for i in REQUIRED_INSTRUMENTS
    if INSTRUMENTS[ExchangeInstrument(Exchange.UNISWAP, i)].dex is not None
}


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

    @staticmethod
    def parse(amount: Decimal, lines: List[str]) -> Optional['CLIQuoteUniswap']:
        quote = {}
        for i, line in enumerate(lines):
            if len(line):
                if field_mapper := CLI_PARSER_LINE_MAPPER.get(i):
                    quote[field_mapper.field_name] = field_mapper.apply(line)
        if len(quote) == 6:
            return CLIQuoteUniswap(amount=amount, **quote)
        return None


CLI_PARSER_LINE_MAPPER = {
    1:  FieldMapper(field_name="best_route", apply=lambda x: x),
    5:  FieldMapper(field_name="quote_in", apply=lambda x: Decimal(x)),
    7:  FieldMapper(field_name="gas_quote", apply=lambda x: Decimal(x[18:])),
    8:  FieldMapper(field_name="gas_usd", apply=lambda x: Decimal(x[11:])),
    9:  FieldMapper(field_name="call_data", apply=lambda x: x[9:]),
    12: FieldMapper(field_name="block_number", apply=lambda x: x[12:]),
}


# async def _quote1(base: ChecksumAddress, quote: ChecksumAddress, amount: Decimal, type_: str) -> Optional[CLIQuoteUniswap]:
#     command = f'{UNI_CLI_PATH}/bin/cli quote -i {quote} -o {base} --amount {amount} --{type_} --recipient 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B --protocols v3'
#     args = shlex.split(command)
#     process = await asyncio.create_subprocess_exec(*args, cwd=UNI_CLI_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     quote = {}
#     field_mapper: Optional[FieldMapper]
#
#     for line_number in range(13):
#         field_mapper = CLI_PARSER_LINE_MAPPER.get(line_number)
#         line = await process.stdout.readline()
#         if field_mapper is not None:
#             normalized_line = ansi_escape.sub('', line.decode("utf-8"))
#             if len(normalized_line):
#                 print('>>>', normalized_line)
#                 quote[field_mapper.field_name] = field_mapper.apply(normalized_line)
#     if len(quote) > 0:
#         return CLIQuoteUniswap(amount=amount, **quote)
#     return None


class UniSwapListener:
    def __init__(self, broker: RMQConnectionAsync, show_stats_every: int) -> None:
        self._broker = broker

        self._started_at = datetime.now()

        self._connetion = web3.Web3(web3.HTTPProvider(JSON_RPC_PROVIDER))
        self._current_block_number = 0

        self._amount = Decimal(10000)
        self._instrument_cache: Dict[Instrument, Tuple[CLIQuoteUniswap, CLIQuoteUniswap]] = {}

        self._stats_instrument_count: Dict[Instrument, int] = {instrument: 0 for instrument in REQUIRED_INSTRUMENTS}
        self._stats_book_ticker_event_count = 0
        self._stats_show_every = show_stats_every
        self._stats_prev_time = 0.

    def _collect_and_show_book_ticker_stats(self, instrument: Instrument) -> None:
        if self._stats_show_every <= 0:
            return
        now = time.time()
        if not self._stats_prev_time:
            self._stats_prev_time = now
            self._start_dt = datetime.now()
        self._stats_instrument_count[instrument] += 1
        self._stats_book_ticker_event_count += 1
        if self._stats_book_ticker_event_count % self._stats_show_every == 0:
            logger.info(
                f'book_ticker {self._stats_show_every / (now - self._stats_prev_time):,.3f} msg/s '
                f'({self._stats_book_ticker_event_count} events from {self._started_at.isoformat()})'
            )
            self._stats_prev_time = now

    async def run(self) -> None:
        while True:
            curr_block_num = self._connetion.eth.block_number
            if self._current_block_number == curr_block_num:
                continue
            logger.info(f'new block {curr_block_num}')
            await self._handle_tick()
            self._current_block_number = curr_block_num

    async def _quote(self, base: ChecksumAddress, quote: ChecksumAddress, is_bid: bool) -> Optional[CLIQuoteUniswap]:
        try:
            args = shlex.split(
                f'{UNI_CLI_PATH}/bin/cli quote'
                f' -i {quote}'
                f' -o {base}'
                f' --amount {self._amount}'
                f' --{"exactIn" if is_bid else "exactOut"}'
                f' --recipient 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B'
                f' --protocols v3'
            )
            process = await asyncio.create_subprocess_exec(*args, cwd=UNI_CLI_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            res = await process.wait()
            lines = []
            for _ in range(13):
                line_b = await process.stdout.readline()
                lines.append(ansi_escape.sub('', line_b.decode("utf-8")))
            return CLIQuoteUniswap.parse(self._amount, lines)
        except Exception as e:
            traceback.print_stack()
            print(str(e))
            pass
            # TODO: show error if needed
        return None

    async def _check_instrument(self, p: DEXExchangeInstrumentParams, i: Instrument) -> Optional[Tuple[CLIQuoteUniswap, CLIQuoteUniswap]]:
        logger.info(f'request to quotes of {i.name}')
        # buy_co = self._quote(p.base.address, p.quote.address, True)
        # sell_co = self._quote(p.base.address, p.quote.address, False)
        # buy = await buy_co
        # sell = await sell_co
        buy, sell = await asyncio.gather(
            self._quote(p.base.address, p.quote.address, True),
            self._quote(p.quote.address, p.base.address, False),
        )
        # buy = await _quote1(p.base.address, p.quote.address, self._amount, 'exactIn')
        # sell = await _quote1(p.base.address, p.quote.address, self._amount, 'exactOut')

        if buy is None or sell is None:
            if buy is None:
                logger.warning(f'{i.name} :: invalid buy')
            if sell is None:
                logger.warning(f'{i.name} :: invalid sell')
            return
        assert buy is not None  # only for mypy
        assert sell is not None  # only for mypy

        # check prices was changed
        prev_buy, prev_sell = self._instrument_cache.get(i, (None, None))
        if prev_buy == buy and prev_sell == sell:
            logger.info(f'{i.name} :: not changed')
            return
        self._instrument_cache[i] = (buy, sell)

        logger.info(f'instrument {i.name} changed')

        self._collect_and_show_book_ticker_stats(i)
        # send to indicator
        await publish_price_topic(self._broker, LastPriceMessage(
            price=InstrumentPrice(
                buy=self._amount / buy.quote_in,
                sell=self._amount / sell.quote_in,
                buy_fee=buy.gas_usd,
                sell_fee=sell.gas_usd,
            ),
            exchange=Exchange.UNISWAP,
            instrument=i
        ))

    async def _handle_tick(self) -> None:
        # TODO: parallel
        # tasks = []
        # for p, i in INSTRUMENT_ARGUMENTS.items():
        #     tasks.append(self._check_instrument(p, i))
        # await asyncio.gather(*tasks)

        # TODO: remove sync
        for p, i in INSTRUMENT_ARGUMENTS.items():
            await self._check_instrument(p, i)


async def main() -> None:
    broker = await message_broker()
    # sync_manager = db_price_parser_uniswap_sync()
    await UniSwapListener(broker, show_stats_every=10).run()


if __name__ == '__main__':
    asyncio.run(main())
