import json
import logging
import subprocess
import traceback
from _decimal import Decimal
from typing import Optional

from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address
from obs_shared.types import TokenRow
from obs_shared.utils.erc20_token_utils import get_token_info_from_json
from web3 import Web3

from src.core.common.base_exchange import BaseExchange
from src.const import ETH_STABLES, PRICE_IMPACT_CALCULATION_VOLUME, UNI_CLI_PATH


class BaseUni(BaseExchange):
    def __init__(self, ) -> None:
        self._web3: Web3
        self.stable_keys = [to_checksum_address(val) for val in ETH_STABLES.values()]

    def get_name(self) -> str:
        pass

    def get_protocol(self) -> str:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _is_stable(self, address: str) -> bool:
        for addr in self.stable_keys:
            if addr == address:
                return True
        return False

    @staticmethod
    def _quote(symbol: str, token0: ChecksumAddress, token1: ChecksumAddress, amount: int, type_: str, protocols: str) -> Optional[dict]:
        command = f'{UNI_CLI_PATH}bin/cli quote-custom --tokenIn {token0} --tokenOut {token1} --amount {amount} --{type_} --recipient 0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B --protocols {protocols}'
        cli_result = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()
        logging.info(f"{symbol}\n{cli_result}")
        output = cli_result[0].decode("utf-8").replace("\n", "")
        try:
            if "Could not find route" in output:
                return None
            pool_pathes = json.loads(output.strip())
            token0_path_chain: TokenRow
            token1_path_chain: TokenRow
            from_token: ChecksumAddress

            for amount in pool_pathes:
                for path_chain in pool_pathes[amount]:
                    from_token = to_checksum_address(path_chain.get("from_token"))
                    token0_path_chain = get_token_info_from_json(path_chain.get("token0"), 5)
                    token1_path_chain = get_token_info_from_json(path_chain.get("token1"), 5)
                    if from_token == token1_path_chain.address:
                        path_chain['token0'] = token1_path_chain
                        path_chain['token1'] = token0_path_chain
                    else:
                        path_chain['token1'] = token1_path_chain
                        path_chain['token0'] = token0_path_chain
            return pool_pathes
        except Exception:
            logging.error(traceback.format_exc())
            return None

    def parse_path(self, pair_symbol: str, token0: TokenRow, token1: TokenRow, type_: str) -> Optional[dict]:
        return self._quote(pair_symbol, token0.address, token1.address, PRICE_IMPACT_CALCULATION_VOLUME, type_, self.get_protocol())

    def parse_price(
        self,
        token0: TokenRow,
        token1: TokenRow,
        is_buy: bool,
        path: dict
    ) -> Decimal:
        raise NotImplementedError()