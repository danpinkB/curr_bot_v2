from inmemory_storage.tg_settings_db.env import SETTINGS_DB__DSN
from inmemory_storage.tg_settings_db.tg_settings_provider import TgSettingsProvider


def tg_settings_db():
    return TgSettingsProvider(SETTINGS_DB__DSN)
