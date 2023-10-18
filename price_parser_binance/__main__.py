import logging
import time
import traceback
from typing import Dict, List, Set

from binance import ThreadedWebsocketManager
from binance.streams import ReconnectingWebsocket

from obs_shared.connection.active_settings_exchange_rconn import ActiveSettingsExchangeRConnection
from obs_shared.connection.price_db_rconn import PriceRConnection
from obs_shared.connection.rabbit_mq_connection import RMQConnection
from obs_shared.types.calculation_price import CalculationPrice
from obs_shared.types.price_row import PriceRow
from price_parser_binance.env import RABBITMQ_QUE__SENDER, REDIS_DSN__SETTINGS, RABBITMQ_DSN__SENDER, REDIS_DSN__PRICE

NAME = "BIN"

setting_rconn: ActiveSettingsExchangeRConnection = ActiveSettingsExchangeRConnection(REDIS_DSN__SETTINGS, NAME, 1)
price_sender: RMQConnection = RMQConnection(RABBITMQ_DSN__SENDER, RABBITMQ_QUE__SENDER)
price_rconn: PriceRConnection = PriceRConnection(REDIS_DSN__PRICE)


def handle_socket_message(msg: Dict):
    data = msg.get("data")
    if data is not None:
        # logging.info(data)
        pair_symbol = data['s']
        price = PriceRow.from_row(data['b'])
        # logging.info(f'{pair_symbol} {price}')
        calc_entity = CalculationPrice(
            group=1,
            symbol=pair_symbol,
            exchange=NAME,
            price=price,
            buy=None
        )
        price_rconn.set_exchange_pair_price(NAME, pair_symbol, price)
        price_sender.send_message(RABBITMQ_QUE__SENDER, calc_entity.to_bytes())
    else:
        traceback.print_stack()
        logging.info(f"{msg}")


if __name__ == '__main__':
    ReconnectingWebsocket.MAX_QUEUE_SIZE = 1_000_000_000_000
    logging.basicConfig(level=logging.INFO)
    twm = ThreadedWebsocketManager()

    twm.MAX_QUEUE_SIZE = 100000
    streams = set()
    new_streams: Set[str]
    try:
        while True:
            new_streams = setting_rconn.get_pairs()
            if len(streams.symmetric_difference(new_streams)) > 0:
                if twm.is_alive():
                    twm.stop()
                    twm.join()
                twm = ThreadedWebsocketManager()
                twm.start()
                streams = new_streams
                twm.start_multiplex_socket(callback=handle_socket_message, streams=[pair.lower() + "@bookTicker" for pair in streams])
            time.sleep(setting_rconn.get_setting().delay_mills/1000)
    finally:
        twm.stop()


