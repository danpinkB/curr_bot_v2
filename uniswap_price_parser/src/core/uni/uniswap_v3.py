from _decimal import Decimal
from typing import Tuple

import web3
from obs_shared.types import TokenRow

from src.const import UNI_V3_QUOTER_ADDRESS
from src.static import uni_v3_quoter_abi
from src.core.uni.base_uni import BaseUni
from src.common import DEXSettings

NAME = "UNIv3"


class UniExchangeV3(BaseUni):
    def __init__(self, provider: web3.providers.JSONBaseProvider) -> None:
        self._web3 = web3.Web3(provider)
        super().__init__()

    def get_name(self) -> str:
        return NAME

    def get_protocol(self) -> str:
        return "v3"

    def parse_price(
            self,
            token0: TokenRow,
            token1: TokenRow,
            is_buy: bool,
            path: dict
    ) -> Decimal:
        web3 = self._web3
        fee: int
        token0_path_chain: Tuple[str, str, str, str]
        token1_path_chain: Tuple[str, str, str, str]
        quoter = web3.eth.contract(UNI_V3_QUOTER_ADDRESS, abi=uni_v3_quoter_abi)
        amount: int = 0
        total: int = 0
        total_token = 0
        for percent, perc_path in path.items():
            if is_buy:
                for path_chain in perc_path:
                    token0_path_chain = path_chain.get("token0")
                    token1_path_chain = path_chain.get("token1")
                    fee = path_chain.get("fee")
                    if amount == 0:
                        amount = int(percent) * int(token0_path_chain[3])
                        total += amount
                    p = quoter.functions.quoteExactInputSingle((token0_path_chain[0], token1_path_chain[0], amount, fee, 0)).call()
                    amount = p[0]
            else:
                for path_chain in reversed(perc_path):
                    token0_path_chain = path_chain.get("token0")
                    token1_path_chain = path_chain.get("token1")
                    fee = path_chain.get("fee")
                    if amount == 0:
                        amount = int(percent) * int(token1_path_chain[3])
                        total += amount
                    p = quoter.functions.quoteExactOutputSingle(
                        (token0_path_chain[0], token1_path_chain[0], amount, fee, 0)).call()
                    amount = p[0]

            total_token += amount
            amount = 0
        if is_buy:
            price = (total / token0.decimals) / (total_token / token1.decimals)
        else:
            price = (total / token1.decimals) / (total_token / token0.decimals)
        return price
