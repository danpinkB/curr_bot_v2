import logging

import aiohttp
import uvicorn
from fastapi import FastAPI

from abstract.const import EXCHANGES
from abstract.instrument import Instrument
from kv_db.db_tg_settings.db_tg_settings import db_tg_settings
from kv_db.db_tg_settings.structures import TelegramSettings
from management_api.env import MANAGEMENT_API_PORT, LAST_PRICE_API_URL


app = FastAPI()


@app.get("/price")
async def get_price(instrument: Instrument) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{LAST_PRICE_API_URL}/price/{instrument}") as response:
            return await response.json()


@app.put("/telegram/db_settings")
async def set_settings(settings: TelegramSettings) -> None:
    await telegram_settings_rconn.set_settings(settings)


@app.get("/telegram/db_settings")
async def get_settings() -> TelegramSettings:
    return await telegram_settings_rconn.get_settings()


@app.get("/exchanges")
async def get_exchanges() -> str:
    return ", ".join([i.name for i in EXCHANGES.values()])


if __name__ == "__main__":
    telegram_settings_rconn = db_tg_settings()
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=MANAGEMENT_API_PORT)

