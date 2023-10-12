import time
from typing import Dict, List

from binance import ThreadedWebsocketManager
from obs_shared.connection import RMQConnection, ActiveSettingsRConnection
from obs_shared.types import CalculationPrice

from src.const import SENDER_RMQ_QUE, \
    SENDER_RMQ_PASSWORD, SENDER_RMQ_USER, SENDER_RMQ_HOST, SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD, RESIDENT_SLEEPER_DELAY

setting_rconn: ActiveSettingsRConnection = ActiveSettingsRConnection(SETTINGS_R_HOST, SETTINGS_R_DB, SETTINGS_R_PASSWORD)
price_sender: RMQConnection = RMQConnection(SENDER_RMQ_HOST, SENDER_RMQ_USER, SENDER_RMQ_PASSWORD)


NAME = "BIN"


def handle_socket_message(msg: Dict):
    data = msg.get("data")
    pair_symbol = data['s']
    price = data['b']
    calc_entity = CalculationPrice(
        group=1,
        symbol=pair_symbol,
        exchange=NAME,
        price=price,
        buy=None
    )
    price_sender.send_message(SENDER_RMQ_QUE, calc_entity.to_bytes())
    # print(f"message type: {msg['e']}")


if __name__ == '__main__':
    twm = ThreadedWebsocketManager()
    streams = list()
    new_streams: List[str]
    try:
        while True:
            new_streams = [pair.lower() + "@bookTicker" for pair in setting_rconn.get_ex_pairs(NAME)]
            if new_streams != streams:
                if twm.is_alive():
                    twm.stop()
                    twm.join()
                twm = ThreadedWebsocketManager()
                twm.start()
                streams = new_streams
                twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)
            time.sleep(RESIDENT_SLEEPER_DELAY)
    finally:
        twm.stop()
    # twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)
    # twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    # or a multiplex socket can be started like this
    # see Binance docs for stream names


