from typing import NamedTuple


class TelegramSettings(NamedTuple):
    percent: float
    calc_volume: int
    messages_delay: int


class TelegramSetting(NamedTuple):
    setting_name: str
    setting_value: str

