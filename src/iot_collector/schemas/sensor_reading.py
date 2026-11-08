from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    device_id: str = Field(min_length=1)
    sequence: int = Field(ge=0)
    temperature: float = Field(ge=-40, le=125)
    humidity: float = Field(ge=0, le=100)
