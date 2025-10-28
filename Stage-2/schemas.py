from pydantic import BaseModel

class CountryRequest(BaseModel):
    name: str
    capital: str | None = None
    region: str | None = None
    population: int
    currency_code: str | None = None
    exchange_rate: float | None = None
    estimated_gdp: float | None = None
    flag_url: str | None = None


class NameRequest(BaseModel):
    name: str

class FilterRequest(BaseModel):
    region: str | None = None
    currency_code: str | None = None
    sort: str | None = None
    