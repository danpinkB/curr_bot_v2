import os
import unittest
from _decimal import Decimal

import web3

from obs_shared.static import uni_v3_quoter_abi
from obs_shared.types.path_row import PathRow, PathRowChain
from obs_shared.types.token_row import TokenRow
from price_parser_uniswap.const import UNI_V3_QUOTER_ADDRESS

web3_conn = web3.Web3(web3.HTTPProvider("http://srv22130.dus4.fastwebserver.de:8545"))


def parse_path_price(
        token0: TokenRow,
        token1: TokenRow,
        is_buy: bool,
        path: PathRow
) -> Decimal:
    fee: int
    from_: TokenRow
    to_: TokenRow
    quoter = web3_conn.eth.contract(UNI_V3_QUOTER_ADDRESS, abi=uni_v3_quoter_abi)
    amount: int = 0
    total: int = 0
    total_token = 0
    for percent, perc_path in path.chains.items():
        if is_buy:
            for path_chain in perc_path:
                from_ = path_chain.token_from
                to_ = path_chain.token_to
                if amount == 0:
                    amount = int(percent) * int(from_.decimals)
                    total += amount
                p = quoter.functions.quoteExactInputSingle(
                    (from_.address, to_.address, amount, path_chain.fee, 0)).call()
                amount = p[0]
        else:
            for path_chain in reversed(perc_path):
                from_ = path_chain.token_from
                to_ = path_chain.token_to
                if amount == 0:
                    amount = int(percent) * int(to_.decimals)
                    total += amount
                p = quoter.functions.quoteExactOutputSingle(
                    (from_.address, to_.address, amount, path_chain.fee, 0)).call()
                amount = p[0]

        total_token += amount
        amount = 0
    if is_buy:
        price = (total / token0.decimals) / (total_token / token1.decimals)
    else:
        price = (total / token1.decimals) / (total_token / token0.decimals)
    return price


class MyTestCase(unittest.TestCase):
    def __init__(self, methodName: str):
        super().__init__(methodName)

    def test_price_calc(self):
        path = PathRow(chains={'10000': [PathRowChain(token_from=TokenRow(address='0x3d6F0DEa3AC3C607B3998e6Ce14b6350721752d9', symbol='CARDS', full_symbol='CARDS', decimals=Decimal('1000000000000000000'), chain=5), token_to=TokenRow(address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', symbol='ETH', full_symbol='WETH', decimals=Decimal('1000000000000000000'), chain=5), fee=10000), PathRowChain(token_from=TokenRow(address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', symbol='ETH', full_symbol='WETH', decimals=Decimal('1000000000000000000'), chain=5), token_to=TokenRow(address='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', symbol='USDC', full_symbol='USDC', decimals=Decimal('1000000'), chain=5), fee=500), PathRowChain(token_from=TokenRow(address='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', symbol='USDC', full_symbol='USDC', decimals=Decimal('1000000'), chain=5), token_to=TokenRow(address='0xdAC17F958D2ee523a2206206994597C13D831ec7', symbol='USDT', full_symbol='USDT', decimals=Decimal('1000000'), chain=5), fee=100)]})
        token0 = TokenRow(address='0x3d6F0DEa3AC3C607B3998e6Ce14b6350721752d9', symbol='CARDS', full_symbol='CARDS', decimals=Decimal('1000000000000000000'), chain=5)
        token1 = TokenRow(address='0xdAC17F958D2ee523a2206206994597C13D831ec7', symbol='USDT', full_symbol='USDT', decimals=Decimal('1000000'), chain=5)
        parse_path_price(token0, token1, True, path)



if __name__ == '__main__':
    unittest.main()
