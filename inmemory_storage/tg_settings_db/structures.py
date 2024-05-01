from typing import NamedTuple, Dict

from pydantic import BaseModel


class TelegramSettings(BaseModel):
    percent: float
    calc_volume: int
    messages_delay: int
