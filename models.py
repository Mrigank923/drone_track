from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from database import Base


class Mine(Base):
    __tablename__ = "mines"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    label = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Pole(Base):
    __tablename__ = "poles"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    label = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DronePosition(Base):
    __tablename__ = "drone_positions"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

class SafePath(Base):
    __tablename__ = "safe_paths"
    id = Column(Integer, primary_key=True, index=True)
    block_latitude = Column(Float, nullable=False)
    block_longitude = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

