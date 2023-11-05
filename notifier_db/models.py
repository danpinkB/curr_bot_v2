from datetime import datetime
from typing import Tuple

from pydantic import BaseModel


class Notification(BaseModel):
    name: str
    message: bytes
    type: str
