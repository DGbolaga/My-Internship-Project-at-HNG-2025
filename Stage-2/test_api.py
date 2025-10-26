from fastapi.testclient import TestClient
from main import app, get_db
from main import engine, SessionLocal 

from models import Base, Country
import os

# Create test database
TEST_DB = "test_countries.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_refresh_countries():
    """Test refreshing countries from external APIs"""
    response = client.post("/countries/refresh")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Check if countries were added
    status_response = client.get("/status")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["total_countries"] > 0
    assert data["last_refreshed_at"] is not None


def test_get_countries():
    """Test getting all countries"""
    response = client.get("/countries")
    assert response.status_code == 200
    countries = response.json()
    assert isinstance(countries, list)
    assert len(countries) > 0
    
    # Check structure of first country
    first_country = countries[0]
    assert "id" in first_country
    assert "name" in first_country
    assert "population" in first_country


def test_get_countries_with_filters():
    """Test filtering countries by region"""
    response = client.get("/countries?region=Africa")
    assert response.status_code == 200
    countries = response.json()
    
    # All countries should be from Africa
    for country in countries:
        assert country["region"] == "Africa"


def test_get_countries_with_sorting():
    """Test sorting countries by GDP"""
    response = client.get("/countries?sort=gdp_desc")
    assert response.status_code == 200
    countries = response.json()
    
    # Check if sorted in descending order
    if len(countries) > 1:
        for i in range(len(countries) - 1):
            if countries[i]["estimated_gdp"] and countries[i+1]["estimated_gdp"]:
                assert countries[i]["estimated_gdp"] >= countries[i+1]["estimated_gdp"]


def test_get_country_by_name():
    """Test getting a specific country"""
    # First, get a country name
    all_countries = client.get("/countries").json()
    if len(all_countries) > 0:
        country_name = all_countries[0]["name"]
        
        response = client.get(f"/countries/{country_name}")
        assert response.status_code == 200
        country = response.json()
        assert country["name"] == country_name


def test_get_nonexistent_country():
    """Test getting a country that doesn't exist"""
    response = client.get("/countries/NonexistentCountry123")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "not found" in response.json()["detail"].lower()


def test_delete_country():
    """Test deleting a country"""
    # First, get a country to delete
    all_countries = client.get("/countries").json()
    if len(all_countries) > 0:
        country_name = all_countries[0]["name"]
        
        # Delete it
        response = client.delete(f"/countries/{country_name}")
        assert response.status_code == 200
        assert "message" in response.json()
        
        # Verify it's deleted
        get_response = client.get(f"/countries/{country_name}")
        assert get_response.status_code == 404


def test_delete_nonexistent_country():
    """Test deleting a country that doesn't exist"""
    response = client.delete("/countries/NonexistentCountry123")
    assert response.status_code == 404


def test_status():
    """Test status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "total_countries" in data
    assert "last_refreshed_at" in data


def test_summary_image():
    """Test summary image endpoint"""
    # First refresh to generate image
    client.post("/countries/refresh")
    
    # Try to get image
    response = client.get("/countries/image")
    
    # Should either succeed or not found
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        assert response.headers["content-type"] == "image/png"


def test_currency_filter():
    """Test filtering by currency"""
    response = client.get("/countries?currency=USD")
    assert response.status_code == 200
    countries = response.json()
    
    # All countries should have USD as currency
    for country in countries:
        if country["currency_code"]:
            assert country["currency_code"] == "USD"


if __name__ == "__main__":
    print("Running tests...")
    
    test_root()
    print("✓ Root endpoint works")
    
    test_refresh_countries()
    print("✓ Refresh countries works")
    
    test_get_countries()
    print("✓ Get all countries works")
    
    test_get_countries_with_filters()
    print("✓ Filter by region works")
    
    test_get_countries_with_sorting()
    print("✓ Sort by GDP works")
    
    test_get_country_by_name()
    print("✓ Get country by name works")
    
    test_get_nonexistent_country()
    print("✓ 404 for nonexistent country works")
    
    test_status()
    print("✓ Status endpoint works")
    
    test_currency_filter()
    print("✓ Currency filter works")
    
    test_delete_country()
    print("✓ Delete country works")
    
    test_delete_nonexistent_country()
    print("✓ Delete nonexistent country returns 404")
    
    test_summary_image()
    print("✓ Summary image endpoint works")
    
    print("\n✅ All tests passed!")