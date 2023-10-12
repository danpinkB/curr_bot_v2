import json
import time
from multiprocessing.managers import ValueProxy
from typing import Set

import requests
from websockets.sync.client import connect


class BinanceExchange:

    def __enter__(self) -> 'BinanceExchange':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def __init__(self, provider_href: str) -> None:
        self._provider_href = provider_href

    def get_name(self) -> str:
        return "BIN"

    def process_arg_string(self, pairs: Set[str]):
        values_str = '['
        len_ = len(pairs)
        for i, symbol in enumerate(pairs):
            if i + 1 < len_:
                values_str += f'"{symbol}",'
            else:
                values_str += f'"{symbol}"'
        values_str += ']'
        return values_str

    def parse_prices(self, pairs: Set[str]) -> None:
        if len(pairs) > 0:
            values_str = self.process_arg_string(pairs)
            with connect(self._provider_href + values_str+"@aggTrade") as ws:
                ws.send(json.dumps({
                  "id": "043a7cf2-bde3-4888-9604-c8ac41fcba4d",
                  "method": "ticker.price",
                  "params": {
                    "symbol": "BNBBTC"
                  }
                }))
                message = ws.recv()
                print(message)
            # pairs_data = websockets. .get(self._provider_href + "/ticker/price", params={"symbols": values_str}).json()
            # #logging.info(pairs_data)
            # for pair in pairs_data:
            #     symbol = str(pair.get("symbol"))
            #     price = pair.get("price")



