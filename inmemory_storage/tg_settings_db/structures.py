from typing import NamedTuple, Dict
from _decimal import Decimal
from pydantic import BaseModel


class TelegramSettings(BaseModel):
    percent: float
    calc_volume: int
    messages_delay: int

    def get_percent(self) -> Decimal:
        return Decimal(self.percent)
