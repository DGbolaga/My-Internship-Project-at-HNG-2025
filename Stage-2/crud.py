from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Country
from datetime import datetime

def get_country_by_name(db: Session, name: str):
    """Get a country by name (case-insensitive)"""
    return db.query(Country).filter(func.lower(Country.name) == func.lower(name)).first()


def create_or_update_country(db: Session, country_data: dict):
    """Create a new country or update if exists"""
    existing_country = get_country_by_name(db, country_data["name"])
    
    if existing_country:
        # Update existing country
        for key, value in country_data.items():
            setattr(existing_country, key, value)
        db.commit()
        db.refresh(existing_country)
        return existing_country
    else:
        # Create new country
        new_country = Country(**country_data)
        db.add(new_country)
        db.commit()
        db.refresh(new_country)
        return new_country


def get_countries(db: Session, region: str = None, currency_code: str = None, sort: str = None):
    """Get all countries with optional filters and sorting"""
    query = db.query(Country)
    
    # Apply filters
    if region:
        query = query.filter(Country.region == region)
    
    if currency_code:
        query = query.filter(Country.currency_code == currency_code)
    
    # Apply sorting
    if sort == "gdp_desc":
        query = query.order_by(Country.estimated_gdp.desc())
    elif sort == "gdp_asc":
        query = query.order_by(Country.estimated_gdp.asc())
    elif sort == "name_asc":
        query = query.order_by(Country.name.asc())
    elif sort == "name_desc":
        query = query.order_by(Country.name.desc())
    elif sort == "population_desc":
        query = query.order_by(Country.population.desc())
    elif sort == "population_asc":
        query = query.order_by(Country.population.asc())
    
    return query.all()


def delete_country(db: Session, name: str):
    """Delete a country by name"""
    country = get_country_by_name(db, name)
    if country:
        db.delete(country)
        db.commit()
        return True
    return False


def get_total_countries(db: Session):
    """Get total number of countries"""
    return db.query(Country).count()


def get_last_refresh_time(db: Session):
    """Get the most recent refresh timestamp"""
    result = db.query(func.max(Country.last_refreshed_at)).scalar()
    return result


def get_top_countries_by_gdp(db: Session, limit: int = 5):
    """Get top countries by estimated GDP"""
    return db.query(Country).filter(Country.estimated_gdp != None).order_by(Country.estimated_gdp.desc()).limit(limit).all()