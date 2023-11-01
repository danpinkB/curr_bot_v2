from _decimal import Decimal
from typing import NamedTuple, Set


class TelegramSettings(NamedTuple):
    percent: Decimal
    calc_volume: int
    messages_delay: int

    @staticmethod
    def from_set(data: Set[str]) -> 'TelegramSettings':
        return TelegramSettings(
            messages_delay=int(data.pop()),
            calc_volume=int(data.pop()),
            percent=Decimal(data.pop())
        )

    def to_message(self) -> str:
        return (f"percent: {self.percent}\n"
                f"calc_volume: {self.calc_volume}\n"
                f"message_delay: {self.messages_delay}")


class TelegramSetting(NamedTuple):
    setting_name: str
    setting_value: str

