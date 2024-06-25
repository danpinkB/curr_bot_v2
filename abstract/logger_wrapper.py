import logging
from abstract.env import ENV

level = ENV.get('LOGLEVEL', 'INFO')


def wrap_logger():
    logging.basicConfig(level=level, datefmt='%Y-%m-%d %H:%M:%S', format="%(asctime)s.%(msecs)d | %(levelname)s | %(module)s | %(message)s")



