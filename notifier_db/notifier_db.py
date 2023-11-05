from sqlalchemy.ext.asyncio import create_async_engine

from notifier_db.env import NOTIFIER_DB__DSN


def notifier_db():
    return create_async_engine(NOTIFIER_DB__DSN, echo=True)

