from _decimal import Decimal
from typing import Dict, Any

from eth_utils import to_checksum_address
from web3.contract import Contract

from obs_shared.types.token_row import TokenRow

known_names = ["WETH"]


class TokenSymbolUtils:
    @staticmethod
    def normalize_token_symbol(token_name: str, token_symbol: str) -> str:
        if token_name is None:
            return token_symbol
        return token_symbol if "Wrapped" not in token_name and token_name not in known_names else token_symbol[1:]


def get_token_info(token_contract: Contract, chain: int) -> TokenRow:
    token_name, token_symbol = token_contract.functions.name().call(), token_contract.functions.symbol().call()
    return TokenRow(
        address=token_contract.address,
        # name=token_name,
        symbol=TokenSymbolUtils.normalize_token_symbol(token_name, token_symbol),
        full_symbol=token_symbol,
        decimals=Decimal(10 ** token_contract.functions.decimals().call()),
        chain=chain
    )


def get_token_info_from_json(token_data: Dict[str, Any], chain: int) -> TokenRow:
    return TokenRow(
        address=to_checksum_address(token_data.get("address")),
        # name=token_name,
        symbol=TokenSymbolUtils.normalize_token_symbol(token_data.get("name"), token_data.get("symbol")),
        full_symbol=token_data.get("symbol"),
        decimals=Decimal(10 ** int(token_data.get("decimals"))),
        chain=chain
    )

