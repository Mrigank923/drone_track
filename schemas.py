from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CoordBase(BaseModel):
    latitude: float = Field(..., example=12.34567)
    longitude: float = Field(..., example=76.54321)


class MineCreate(CoordBase):
    label: Optional[str] = None
    auth_key: str


class PoleCreate(CoordBase):
    label: Optional[str] = None
    auth_key: str


class DroneCreate(CoordBase):
    recorded_at: Optional[datetime] = None
    auth_key: str


class CoordOut(CoordBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class SafePathCreate(BaseModel):
    block_latitude: float = Field(..., example=12.34567)
    block_longitude: float = Field(..., example=76.54321)
    auth_key: str


class SafePathOut(CoordBase):
    id: str
    model_config = ConfigDict(from_attributes=True)
    recorded_at: datetime


    