import logging
import time
from typing import Set, Dict

import requests
from eth_utils import to_checksum_address

from obs_shared.connection.active_settings_exchange_rconn import ActiveSettingsExchangeRConnection
from obs_shared.connection.info_db_rconn import InfoSettingsRConnection
from obs_shared.types.pair_row import PairRow
from obs_shared.types.token_row import TokenRow
from obs_shared.utils.erc20_token_utils import get_token_info_from_json
from pairs_parser_uniswap.const import CHAIN, STABLES
from pairs_parser_uniswap.env import REDIS_DSN__INFO, REDIS_DSN__SETTINGS

NAME = "UNIv3"
setting_rconn: ActiveSettingsExchangeRConnection = ActiveSettingsExchangeRConnection(REDIS_DSN__SETTINGS, NAME, 1)
info_rconn: InfoSettingsRConnection = InfoSettingsRConnection(REDIS_DSN__INFO, NAME, CHAIN)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    last_parsed_pairs_time = 0
    t12_hours = 60*60*12
    symbols: Set[str] = set()
    stable_addresses = [to_checksum_address(val) for val in STABLES.values()]
    stable_tokens: Dict[str, TokenRow] = dict()
    tokens: Dict[str, TokenRow] = dict()
    while True:
        now = time.time()
        prev_pairs = setting_rconn.get_pairs()
        banned_pairs = setting_rconn.get_banned_pairs()
        if now - last_parsed_pairs_time >= t12_hours:
            symbols.clear()
            tokens.clear()
            for token in requests.get("https://tokens.coingecko.com/uniswap/all.json").json().get("tokens"):
                parsed_token = get_token_info_from_json(token, 5)
                if parsed_token.address in stable_addresses:
                    stable_tokens[parsed_token.address] = parsed_token
                else:
                    tokens[parsed_token.address] = parsed_token
                info_rconn.set_token_info(parsed_token)
            stable_val: TokenRow
            token_val: TokenRow

            for stable_key, stable_val in stable_tokens.items():
                for token_key, token_val in tokens.items():
                    symbol = f'{token_val.symbol}{stable_val.symbol}'
                    pair = PairRow(symbol=symbol, token0=token_val.address, token1=stable_val.address, chain=CHAIN)
                    info_rconn.set_pair_info(pair)
                    symbols.add(symbol)
            info_rconn.add_ex_pairs(NAME, symbols)
        else:
            symbols = info_rconn.get_ex_pairs(NAME)
        active_pairs = {symbol for symbol in symbols if symbol not in banned_pairs}
        general_pairs = set()
        for cex_exchange in setting_rconn.get_group_exchanges(1):
            cex_pairs = info_rconn.get_ex_pairs(cex_exchange)
            cex_banned_pairs = setting_rconn.get_exchange_banned_pairs(cex_exchange)
            general_pairs = general_pairs.union(active_pairs.intersection({pair for pair in cex_pairs if pair not in cex_banned_pairs}))
        if len(general_pairs) > 0:
            setting_rconn.deactivate_ex_pairs(NAME, prev_pairs.difference(general_pairs))
            setting_rconn.activate_ex_pairs(NAME, general_pairs)

        time.sleep(setting_rconn.get_setting().delay_mills/1000)



