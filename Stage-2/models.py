from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False, index=True)
    capital = Column(String, nullable=True)
    region = Column(String, nullable=True, index=True)
    population = Column(Integer, nullable=False)
    currency_code = Column(String, nullable=True, index=True)
    exchange_rate = Column(Float, nullable=True)
    estimated_gdp = Column(Float, nullable=True)
    flag_url = Column(String, nullable=True)
    last_refreshed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Country(name='{self.name}', region='{self.region}')>"