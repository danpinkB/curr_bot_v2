import time
from _decimal import Decimal
from typing import Set

import requests
from obs_shared.connection import ActiveSettingsRConnection, InfoSettingsRConnection

from src.env import SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD, BINANCE_API, DAILY_RATE, INFO_R_HOST, \
    INFO_R_DB, INFO_R_PASSWORD, RESIDENT_SLEEPER_DELAY

NAME = "BIN"
setting_rconn: ActiveSettingsRConnection = ActiveSettingsRConnection(SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD, NAME, 1)
info_rconn: InfoSettingsRConnection = InfoSettingsRConnection(INFO_R_HOST, INFO_R_DB, INFO_R_PASSWORD, NAME)

if __name__ == '__main__':
    last_parsed_pairs_time = 0
    t12_hours = 60*60*12
    symbols: Set[str]
    while True:
        now = time.time()
        prev_pairs = setting_rconn.get_pairs()
        banned_pairs = setting_rconn.get_banned_pairs()
        if now - last_parsed_pairs_time >= t12_hours:
            res = requests.get(BINANCE_API + "/ticker/24hr").json()
            symbols = {pair.get("symbol") for pair in res if "USDT" in pair.get("symbol") and Decimal(pair.get("volume")) > DAILY_RATE and pair.get("symbol")}
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
            setting_rconn.deactivate_ex_pairs(prev_pairs.difference(general_pairs))
            setting_rconn.activate_ex_pairs(general_pairs)

        time.sleep(RESIDENT_SLEEPER_DELAY)



