import json
import logging
from typing import Dict, Any

import aiohttp
import uvicorn
from fastapi import FastAPI

from abstract.const import EXCHANGES
from abstract.instrument import Instrument
from kv_db.db_tg_settings.db_tg_settings import db_tg_settings
from kv_db.db_tg_settings.structures import TelegramSettings
from management_api.env import MANAGEMENT_API_PORT, LAST_PRICE_API_URL

app = FastAPI()

JSON_HEADERS = {'Content-Type': 'application/json'}


@app.get("/price")
async def get_price(instrument: int) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{LAST_PRICE_API_URL}/price?instrument={instrument}", headers=JSON_HEADERS) as response:
            return await response.json(content_type=None)


@app.post("/telegram/settings")
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

