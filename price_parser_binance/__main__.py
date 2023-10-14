import logging
import time
from typing import Dict, List

from binance import ThreadedWebsocketManager

from obs_shared.connection.active_settings_exchange_rconn import ActiveSettingsExchangeRConnection
from obs_shared.connection.rabbit_mq_connection import RMQConnection
from obs_shared.types.calculation_price import CalculationPrice
from obs_shared.types.price_row import PriceRow
from price_parser_binance.env import RABBITMQ_QUE__SENDER, REDIS_DSN__SETTINGS, RABBITMQ_DSN__SENDER

NAME = "BIN"

setting_rconn: ActiveSettingsExchangeRConnection = ActiveSettingsExchangeRConnection(REDIS_DSN__SETTINGS, NAME, 1)
price_sender: RMQConnection = RMQConnection(RABBITMQ_DSN__SENDER, RABBITMQ_QUE__SENDER)


def handle_socket_message(msg: Dict):
    data = msg.get("data")
    if data is not None:
        # logging.info(data)
        pair_symbol = data['s']
        price = PriceRow.from_row(data['b'])
        calc_entity = CalculationPrice(
            group=1,
            symbol=pair_symbol,
            exchange=NAME,
            price=price,
            buy=None
        )
        price_sender.send_message(RABBITMQ_QUE__SENDER, calc_entity.to_bytes())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    twm = ThreadedWebsocketManager()
    streams = list()
    new_streams: List[str]
    try:
        while True:
            new_streams = [pair.lower() + "@bookTicker" for pair in setting_rconn.get_pairs()]
            if new_streams != streams:
                if twm.is_alive():
                    twm.stop()
                    twm.join()
                twm = ThreadedWebsocketManager()
                twm.start()
                streams = new_streams
                twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)
            time.sleep(setting_rconn.get_setting().delay_mills/1000)
    finally:
        twm.stop()


