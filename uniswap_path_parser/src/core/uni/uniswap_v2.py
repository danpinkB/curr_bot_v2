from _decimal import Decimal
from typing import Tuple

from eth_typing import ChecksumAddress
from obs_shared.types import TokenRow

from src.core.uni.base_uni import BaseUni
from src.const import UNI_V2_ROUTER_ADDRESS

NAME = "UNIv2"


class UniExchangeV2(BaseUni):
    def __init__(self) -> None:
        super().__init__()

    def get_name(self) -> str:
        return NAME

    def get_protocol(self) -> str:
        return "v2"

    def parse_price(
        self,
        token0: TokenRow,
        token1: TokenRow,
        is_buy: bool,
        path: dict
    ) -> Decimal:
        web3 = settings.create_connection()
        quoter = web3.eth.contract(address=UNI_V2_ROUTER_ADDRESS, abi=uni_v2_router_abi)
        amount = 0
        total = 0
        total_token: int = 0
        token0_path_chain: Tuple[str, str, str, str]
        token1_path_chain: Tuple[str, str, str, str]
        p: list

        for percent in path:
            if is_buy:
                for path_chain in path[percent]:
                    token0_path_chain = path_chain.get("token0")
                    token1_path_chain = path_chain.get("token1")
                    if amount == 0:
                        amount = int(percent) * int(token0_path_chain[3])
                        total += amount
                    p = quoter.functions.getAmountsOut(amount, [token0_path_chain[0], token1_path_chain[0]]).call()
                    amount = p[1]
            else:
                for path_chain in reversed(path[percent]):
                    token0_path_chain = path_chain.get("token0")
                    token1_path_chain = path_chain.get("token1")
                    if amount == 0:
                        amount = int(percent) * int(token0_path_chain[3])
                        total += amount
                    p = quoter.functions.getAmountsIn(amount, [token0_path_chain[0], token1_path_chain[0]]).call()
                    amount = p[0]
            total_token += amount
            amount = 0
        if is_buy:
            price = (total / token0.decimals) / (total_token / token1.decimals)
        else:
            price = (total / token1.decimals) / (total_token / token0.decimals)
        return price


def get_liq(token: ChecksumAddress, token_dec: Decimal, address: ChecksumAddress, settings: DEXSettings) -> Decimal:
    return Decimal(settings.create_connection().eth.contract(token, abi=erc_20_abi).functions.balanceOf(address).call()) / token_dec