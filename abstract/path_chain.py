from decimal import Decimal
from typing import NamedTuple, List


class CLIQuoteUniswap(NamedTuple):
    best_route: str
    quote_in: Decimal
    gas_quote: Decimal
    gas_usd: Decimal
    call_data: str
    block_number: int


class PathChain(NamedTuple):
    version: str
    percent: float
    pools: List[str]

    @staticmethod
    def from_cli(data: CLIQuoteUniswap) -> List['PathChain']:
        # chains = []
        #
        # for entry in input_string.split(', '):
        #     parts = entry.split(' ')
        #     version = parts[0][1:-1]
        #     percent = float(parts[1][:-1])
        #
        #     sub_chains_raw = parts[2:]
        #     sub_chains = [pool[1:-1] for pool in sub_chains_raw if pool.startswith('[') and pool.endswith(']')]
        #
        #     chains.append(PathChain(version=version, percent=percent, subchains=sub_chains))
        return [
            PathChain(
                version=parts[0][1:-1],
                percent=float(parts[1][:-1]),
                pools=[pool[1:-1] for pool in parts[2:] if pool.startswith('[') and pool.endswith(']')]
            )
            for parts in [entry.split(' ') for entry in data.best_route.split(', ')]
        ]

