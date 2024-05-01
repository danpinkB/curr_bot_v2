import logging
from typing import Mapping

import aiohttp
import uvicorn
from fastapi import FastAPI

from abstract.const import EXCHANGES
from abstract.instrument import Instrument
from inmemory_storage.tg_settings_db.structures import TelegramSettings
from inmemory_storage.tg_settings_db.tg_settings_db import tg_settings_db
from management_api.env import MANAGEMENT_API_PORT, LAST_PRICE_API_URL


app = FastAPI()


@app.get("/price/{instrument}")
async def get_price(instrument: Instrument) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{LAST_PRICE_API_URL}/price", params={"instrument": instrument}) as response:
            return await response.json()


@app.put("/telegram/settings")
async def set_settings(settings: TelegramSettings):
    await telegram_settings_rconn.set_settings(settings)
    return "ok"


@app.get("/telegram/settings")
async def get_settings() -> TelegramSettings:
    return await telegram_settings_rconn.get_settings()


@app.get("/exchanges")
async def get_exchanges() -> str:
    return ", ".join([i.name for i in EXCHANGES.values()])


if __name__ == "__main__":
    telegram_settings_rconn = tg_settings_db()
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=MANAGEMENT_API_PORT)

