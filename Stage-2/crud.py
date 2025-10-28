from models import Country
from sqlalchemy import func
from sqlalchemy.orm import Session
from schemas import FilterRequest

def add_countries(db: Session, country_data: dict, commit: bool = True):
    """
    Creates or updates a country record in the database.
    Called during /countries/refresh for each country.
    """
    existing_country = db.query(Country).filter(Country.name == country_data["name"]).first()

    if existing_country:
        # Update existing record
        for key, value in country_data.items():
            setattr(existing_country, key, value)
    else:
        db.add(Country(**country_data))

    if commit:
        db.commit()


def get_all_countries(db: Session):
    """Gets all countries from database."""
    return db.query(Country).all()


def get_all_countries_by_filters(db: Session, filters: FilterRequest):
    """Gets all countries by filters: region, currency, sort."""
    query = db.query(Country)

    # Apply filters
    if filters.region is not None:
        query = query.filter(Country.region == filters.region)
    if filters.currency_code:
        query = query.filter(Country.currency_code == filters.currency_code)

    # Apply sorting
    if filters.sort == "gdp_desc":
        query = query.order_by(Country.estimated_gdp.desc())
    elif filters.sort == "gdp_asc":
        query = query.order_by(Country.estimated_gdp.asc())
    elif filters.sort == "name_asc":
        query = query.order_by(Country.name.asc())
    elif filters.sort == "name_desc":
        query = query.order_by(Country.name.desc())
    elif filters.sort == "population_desc":
        query = query.order_by(Country.population.desc())
    elif filters.sort == "population_asc":
        query = query.order_by(Country.population.asc())

    return query.all()


def get_a_country(db: Session, name: str):
    """Returns information of a single country."""
    return db.query(Country).filter(func.lower(Country.name) == name.lower()).first()


def delete_a_country(db: Session, name: str):
    """Deletes a country by name."""
    country = db.query(Country).filter(func.lower(Country.name) == name.lower()).first()
    if country:
        db.delete(country)
        db.commit()
        return True
    return False


def get_status(db: Session):
    """Returns total number of countries and time of last refresh."""
    total_countries = db.query(func.count(Country.id)).scalar()
    latest_refresh_at = db.query(func.max(Country.last_refreshed_at)).scalar()

    return {
        "total_countries": total_countries,
        "last_refreshed_at": latest_refresh_at,
    }


def generate_summary(db: Session):
    """Generates and saves a summary image using get_status and top countries."""
    import os, io
    from urllib.request import urlopen
    from PIL import Image, ImageDraw, ImageFont
    import cairosvg

    status = get_status(db)
    total_countries = status["total_countries"]
    last_refresh = status["last_refreshed_at"]

    # Get top countries by GDP
    top_countries = (
        db.query(Country)
        .order_by(Country.estimated_gdp.desc())
        .limit(5)
        .all()
    )

    # Create blank image
    width, height = 800, 650
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)
    font_large = font_medium = font_small = ImageFont.load_default()

    # Header
    draw.text((50, 50), "Country Summary Report", fill="black", font=font_large)
    draw.text((50, 100), f"Total Countries: {total_countries}", fill="black", font=font_medium)
    draw.text(
        (50, 140),
        f"Last Refreshed: {last_refresh.strftime('%Y-%m-%d %H:%M:%S UTC') if last_refresh else 'N/A'}",
        fill="gray",
        font=font_small,
    )

    # Top countries
    draw.text((50, 200), "Top 5 Countries by Estimated GDP:", fill="black", font=font_medium)

    y_offset = 250
    for i, country in enumerate(top_countries, 1):
        flag_x, flag_size = 50, 40
        try:
            if country.flag_url:
                with urlopen(country.flag_url, timeout=5) as response:
                    flag_data = response.read()

                    # Convert SVGs to PNGs for Pillow
                    if country.flag_url.endswith(".svg"):
                        flag_data = cairosvg.svg2png(bytestring=flag_data)

                    flag_img = Image.open(io.BytesIO(flag_data)).convert("RGB")
                    flag_img = flag_img.resize((flag_size, flag_size))
                    img.paste(flag_img, (flag_x, y_offset))
            else:
                raise Exception("No flag found")

        except Exception as e:
            # Draw empty placeholder box if something fails
            draw.rectangle(
                [flag_x, y_offset, flag_x + flag_size, y_offset + flag_size],
                outline="gray",
                width=2,
            )

        # Add text beside the flag
        gdp_text = f"{country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
        text = f"{i}. {country.name} - ${gdp_text}"
        draw.text((flag_x + flag_size + 15, y_offset + 10), text, fill="black", font=font_small)

        y_offset += 60

    # Save image
    os.makedirs("cache", exist_ok=True)
    img.save("cache/summary.png")

    return "cache/summary.png"
