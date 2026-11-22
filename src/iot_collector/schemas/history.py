from pydantic import BaseModel


class HistoryPoint(BaseModel):
    timestamp: int
    value: float


class HistoryResponse(BaseModel):
    device_id: str
    range: str
    temperature: list[HistoryPoint]
    humidity: list[HistoryPoint]
