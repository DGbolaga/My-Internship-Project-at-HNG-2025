from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
import requests
import random
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont
from database import engine, SessionLocal
from models import Base, Country
import crud

# Get port from environment (Railway sets this)
PORT = int(os.getenv("PORT", 8000))

# Create tables
Base.metadata.create_all(bind=engine)

# Create cache directory
os.makedirs("cache", exist_ok=True)

app = FastAPI(title="Country Currency & Exchange API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Country Currency & Exchange API", "docs": "/docs"}


@app.post("/countries/refresh")
def refresh_countries():
    """Fetch countries and exchange rates, then cache in database"""
    db = next(get_db())
    
    try:
        # Fetch countries data
        countries_response = requests.get(
            "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies",
            timeout=10
        )
        if countries_response.status_code != 200:
            raise HTTPException(
                status_code=503,
                detail={"error": "External data source unavailable", "details": "Could not fetch data from restcountries.com"}
            )
        countries_data = countries_response.json()
        
        # Fetch exchange rates
        exchange_response = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=10
        )
        if exchange_response.status_code != 200:
            raise HTTPException(
                status_code=503,
                detail={"error": "External data source unavailable", "details": "Could not fetch data from open.er-api.com"}
            )
        exchange_data = exchange_response.json()
        exchange_rates = exchange_data.get("rates", {})
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail={"error": "External data source unavailable", "details": str(e)}
        )
    
    # Process each country
    for country in countries_data:
        name = country.get("name")
        capital = country.get("capital")
        region = country.get("region")
        population = country.get("population")
        flag_url = country.get("flag")
        currencies = country.get("currencies", [])
        
        # Handle currency
        currency_code = None
        exchange_rate = None
        estimated_gdp = 0
        
        if currencies and len(currencies) > 0:
            currency_code = currencies[0].get("code")
            if currency_code and currency_code in exchange_rates:
                exchange_rate = exchange_rates[currency_code]
                # Calculate estimated GDP
                random_multiplier = random.uniform(1000, 2000)
                estimated_gdp = (population * random_multiplier) / exchange_rate
        
        # Create or update country
        country_data = {
            "name": name,
            "capital": capital,
            "region": region,
            "population": population,
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": flag_url,
            "last_refreshed_at": datetime.utcnow()
        }
        
        crud.create_or_update_country(db, country_data)
    
    # Generate summary image
    generate_summary_image(db)
    
    return {"message": "Countries refreshed successfully"}


@app.get("/countries")
def get_countries(
    region: str = Query(None),
    currency: str = Query(None),
    sort: str = Query(None)
):
    """Get all countries with optional filters and sorting"""
    db = next(get_db())
    countries = crud.get_countries(db, region=region, currency_code=currency, sort=sort)
    
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
def get_country(name: str):
    """Get a single country by name"""
    db = next(get_db())
    country = crud.get_country_by_name(db, name)
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    return {
        "id": country.id,
        "name": country.name,
        "capital": country.capital,
        "region": country.region,
        "population": country.population,
        "currency_code": country.currency_code,
        "exchange_rate": country.exchange_rate,
        "estimated_gdp": country.estimated_gdp,
        "flag_url": country.flag_url,
        "last_refreshed_at": country.last_refreshed_at.isoformat() if country.last_refreshed_at else None
    }


@app.delete("/countries/{name}")
def delete_country(name: str):
    """Delete a country by name"""
    db = next(get_db())
    deleted = crud.delete_country(db, name)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Country not found")
    
    return {"message": f"Country '{name}' deleted successfully"}


@app.get("/status")
def get_status():
    """Get total countries and last refresh timestamp"""
    db = next(get_db())
    total = crud.get_total_countries(db)
    last_refresh = crud.get_last_refresh_time(db)
    
    return {
        "total_countries": total,
        "last_refreshed_at": last_refresh.isoformat() if last_refresh else None
    }


@app.get("/countries/image")
def get_summary_image():
    """Serve the generated summary image"""
    image_path = "cache/summary.png"
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Summary image not found")
    
    return FileResponse(image_path, media_type="image/png")


def generate_summary_image(db):
    """Generate summary image with country stats and flags"""
    import io
    from urllib.request import urlopen
    
    # Get data
    total_countries = crud.get_total_countries(db)
    top_countries = crud.get_top_countries_by_gdp(db, limit=5)
    last_refresh = datetime.utcnow()
    
    # Create image
    width, height = 800, 650
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fall back to basic if not available
    try:
        # Try multiple common font paths
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        ]
        font_large = None
        for path in font_paths:
            if os.path.exists(path):
                font_large = ImageFont.truetype(path, 32)
                font_medium = ImageFont.truetype(path, 24)
                font_small = ImageFont.truetype(path, 18)
                break
        if font_large is None:
            raise Exception("No fonts found")
    except:
        # Use default font as fallback
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw header
    draw.text((50, 50), "Country Summary Report", fill='black', font=font_large)
    draw.text((50, 100), f"Total Countries: {total_countries}", fill='black', font=font_medium)
    draw.text((50, 140), f"Generated: {last_refresh.strftime('%Y-%m-%d %H:%M:%S UTC')}", fill='gray', font=font_small)
    
    # Draw top countries
    draw.text((50, 200), "Top 5 Countries by Estimated GDP:", fill='black', font=font_medium)
    
    y_offset = 250
    for i, country in enumerate(top_countries, 1):
        # Try to fetch and display flag
        flag_x = 50
        flag_size = 40
        
        if country.flag_url:
            try:
                # Download flag image
                with urlopen(country.flag_url, timeout=5) as response:
                    flag_data = response.read()
                    flag_img = Image.open(io.BytesIO(flag_data))
                    
                    # Resize flag to fit
                    flag_img = flag_img.resize((flag_size, flag_size), Image.Resampling.LANCZOS)
                    
                    # Paste flag on image
                    img.paste(flag_img, (flag_x, y_offset))
            except:
                # If flag download fails, draw a placeholder box
                draw.rectangle([flag_x, y_offset, flag_x + flag_size, y_offset + flag_size], 
                             outline='gray', width=2)
        else:
            # Draw placeholder if no flag URL
            draw.rectangle([flag_x, y_offset, flag_x + flag_size, y_offset + flag_size], 
                         outline='gray', width=2)
        
        # Draw country info next to flag
        gdp_formatted = f"{country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
        text = f"{i}. {country.name} - ${gdp_formatted}"
        draw.text((flag_x + flag_size + 15, y_offset + 10), text, fill='black', font=font_small)
        y_offset += 60
    
    # Save image
    img.save("cache/summary.png")