import unittest
from _decimal import Decimal

import web3

from net_node import uni_v3_quoter_abi
from obs_shared.mytypes.path_row import PathRow
from obs_shared.mytypes.token_row import TokenRow
from path_parser_uniswap.const import UNI_V3_QUOTER_ADDRESS

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
                from_ = path_chain.quote
                to_ = path_chain.base
                if amount == 0:
                    amount = int(percent) * int(from_.decimals)
                    total += amount
                p = quoter.functions.quoteExactInputSingle(
                    (from_.address, to_.address, amount, path_chain.fee, 0)).call()
                amount = p[0]
        else:
            for path_chain in reversed(perc_path):
                from_ = path_chain.quote
                to_ = path_chain.base
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


if __name__ == '__main__':
    unittest.main()
