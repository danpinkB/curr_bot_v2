import logging
import time
from _decimal import Decimal
from typing import Set

import requests

from obs_shared.connection.active_settings_exchange_rconn import ActiveSettingsExchangeRConnection
from obs_shared.connection.info_db_rconn import InfoSettingsRConnection
from pairs_parser_binance.env import REDIS_DSN__INFO, REDIS_DSN__SETTINGS, BINANCE_API

NAME = "BIN"
setting_rconn: ActiveSettingsExchangeRConnection = ActiveSettingsExchangeRConnection(REDIS_DSN__SETTINGS, NAME, 1)
info_rconn: InfoSettingsRConnection = InfoSettingsRConnection(REDIS_DSN__INFO, NAME)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    last_parsed_pairs_time = 0
    t12_hours = 60*60*12
    symbols: Set[str]
    while True:
        now = time.time()
        prev_pairs = setting_rconn.get_pairs()
        banned_pairs = setting_rconn.get_banned_pairs()
        settings = setting_rconn.get_setting()
        if now - last_parsed_pairs_time >= t12_hours:
            res = requests.get(BINANCE_API + "/ticker/24hr").json()
            symbols = {pair.get("symbol") for pair in res if "USDT" in pair.get("symbol") and Decimal(pair.get("volume")) > Decimal(settings.rvolume) and pair.get("symbol")}
            info_rconn.add_ex_pairs(NAME, symbols)
        else:
            symbols = info_rconn.get_ex_pairs(NAME)
        active_pairs = {symbol for symbol in symbols if symbol not in banned_pairs}
        general_pairs = set()
        for dex_exchange in setting_rconn.get_group_exchanges(0):
            dex_pairs = info_rconn.get_ex_pairs(dex_exchange)
            dex_banned_pairs = setting_rconn.get_exchange_banned_pairs(dex_exchange)
            general_pairs = general_pairs.union(active_pairs.intersection({pair for pair in dex_pairs if pair not in dex_banned_pairs}))
        if len(general_pairs) > 0:
            setting_rconn.deactivate_pairs(prev_pairs.difference(general_pairs))
            setting_rconn.activate_pairs(general_pairs)

        time.sleep(settings.delay_mills/1000)



