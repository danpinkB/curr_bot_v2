from kv_db.db_tg_settings.env import DB_TG_SETTINGS__DSN
from kv_db.db_tg_settings.tg_settings_provider import TgSettingsProvider


def db_tg_settings():
    return TgSettingsProvider(DB_TG_SETTINGS__DSN)
