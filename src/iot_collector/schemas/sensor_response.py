from datetime import datetime

from pydantic import BaseModel


class SensorResponse(BaseModel):
    device_id: str
    sequence: int
    temperature: float
    humidity: float
    last_seen: datetime
    is_stale: bool
