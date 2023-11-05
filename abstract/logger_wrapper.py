import logging
import os.path
import pathlib

from abstract.env import ENV
from abstract.path_const import ROOT

level = ENV.get('LOGLEVEL', 'INFO')


def wrap_logger(file: str) -> logging.Logger:
    logging.basicConfig(
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S',
        format="%(asctime)s.%(msecs)s | %(name)s | %(module)s | %(levelname)s | %(message)s",
    )
    logger_name = str(pathlib.Path(file.removesuffix('.py')).relative_to(ROOT)).replace(os.sep, '.')
    return logging.getLogger(logger_name)
