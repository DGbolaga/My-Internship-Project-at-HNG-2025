from db import Base
from sqlalchemy import Integer, Column, String, Float, DateTime, func

class Country(Base):
    __tablename__ = "Countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name=Column(String, nullable=False)
    capital=Column(String, nullable=True)
    region=Column(String, nullable=True)
    population=Column(Integer, nullable=False)
    currency_code=Column(String, nullable=True)
    exchange_rate=Column(Float, nullable=True)
    estimated_gdp=Column(Float, nullable=True)
    flag_url=Column(String, nullable=True)
    last_refreshed_at=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
