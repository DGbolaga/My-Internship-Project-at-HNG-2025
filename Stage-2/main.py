from fastapi import FastAPI, Depends, status, Request, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from crud import add_countries, get_a_country, get_all_countries_by_filters, delete_a_country, get_status, generate_summary
from models import Country
from schemas import FilterRequest
from db import get_db
from datetime import datetime, timezone
import requests, os, random

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation failed", "details": exc.errors()},
    )


@app.get("/")
def root():
    return {"message": "Country Currency & Exchange API", "docs": "/docs"}


@app.post("/countries/refresh")
async def refresh(db: Session = Depends(get_db)):
    """
    Fetches latest countries and exchange rates, updates the database,
    and generates a summary image.
    """

    countries_api = os.getenv("COUNTRIES_API")
    exchange_api = os.getenv("EXCHANGE_RATES_API")

    try:
        # Fetch countries data
        countries_response = requests.get(countries_api, timeout=10)
        if countries_response.status_code != 200:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "External data source unavailable",
                    "details": f"Could not fetch data from {countries_api}",
                },
            )

        # Fetch exchange rates
        exchange_response = requests.get(exchange_api, timeout=10)
        if exchange_response.status_code != 200:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "External data source unavailable",
                    "details": f"Could not fetch data from {exchange_api}",
                },
            )

    except requests.exceptions.RequestException:
        # Handles timeout, connection error, etc.
        return JSONResponse(
            status_code=503,
            content={
                "error": "External data source unavailable",
                "details": f"Could not fetch data from {countries_api if 'countries' in locals() else exchange_api}",
            },
        )

    # Parse valid data only if both APIs succeeded
    countries_data = countries_response.json()
    exchange_data = exchange_response.json()
    exchange_rates = exchange_data.get("rates", {})

    # Process each country
    for country in countries_data:
        name = country.get("name")
        capital = country.get("capital")
        region = country.get("region")
        population = country.get("population")
        flag_url = country.get("flag")
        currencies = country.get("currencies", [])

        # Handle currency and GDP estimation
        currency_code = None
        exchange_rate = None
        estimated_gdp = 0

        if currencies and len(currencies) > 0:
            currency_code = currencies[0].get("code")
            if currency_code and currency_code in exchange_rates:
                exchange_rate = exchange_rates[currency_code]
                random_multiplier = random.uniform(1000, 2000)
                estimated_gdp = (population * random_multiplier) / exchange_rate

        # Prepare country data
        country_data = {
            "name": name,
            "capital": capital,
            "region": region,
            "population": population,
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": flag_url,
            "last_refreshed_at": datetime.now(timezone.utc),
        }

        # Add or update country
        add_countries(db=db, country_data=country_data, commit=False)

    # Commit all changes at once
    db.commit()

    # Generate summary image
    generate_summary(db)

    return {"message": "Countries refreshed successfully"}



@app.get("/status")
async def show_status(db: Session=Depends(get_db)):
    """
    returns json containing number of countries and last refreshed time.
    """
    return get_status(db)

@app.get("/countries/image")
async def show_summary():
    """
    redirects to endpoint: GET /countries/image
    shows generated image at redirected endpoint
    return json error if image doesn't exist.
    """
    image_path = "cache/summary.png"
    
    if not os.path.exists(image_path):
        return JSONResponse(status_code=404, content={"error": "Summary image not found"})
    
    return FileResponse(image_path, media_type="image/png")
    

@app.get("/countries")
async def countries_by_filter(region: str = Query(None), currency: str = Query(None), sort: str = Query(None), db: Session=Depends(get_db)):
    """
    returns countries based on filters.
    """
    filters = FilterRequest(region=region, currency_code=currency, sort=sort)
    countries = get_all_countries_by_filters(db=db, filters=filters)
    return [
        {
            "id": c.id,
            "name": c.name,
            "capital": c.capital,
            "region": c.region,
            "population": c.population,
            "currency_code": c.currency_code,
            "exchange_rate": c.exchange_rate,
            "estimated_gdp": c.estimated_gdp,
            "flag_url": c.flag_url,
            "last_refreshed_at": c.last_refreshed_at.isoformat() if c.last_refreshed_at else None
        }
        for c in countries
    ]


@app.get("/countries/{name}")
async def get_country(name: str, db: Session=Depends(get_db)):
    """
    get a country by name from database
    """

    query = get_a_country(db=db, name=name)
    if not query:
        return JSONResponse(
            status_code=404,
            content={"error": "Country not found"}
        )
    return query

@app.delete("/countries/{name}")
async def delete_country(name: str, db: Session=Depends(get_db)):
    """
    delete a country from database.
    """
    deleted = delete_a_country(db=db, name=name)
    if not deleted:
        return JSONResponse(
            status_code=404,
            content={"error": "Country not found"}
        )
    
    return {"message": f"Country '{name}' deleted successfully"}

    