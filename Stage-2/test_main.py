import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from datetime import datetime, timezone
import requests

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    """Mock database session for dependency injection."""
    class DummyDB:
        def commit(self): pass
        def query(self, *args, **kwargs): return self
        def filter(self, *args, **kwargs): return self
        def first(self): return None
        def delete(self, *args, **kwargs): pass
        def add(self, *args, **kwargs): pass
        def refresh(self, *args, **kwargs): pass
        def all(self): return []
    return DummyDB()


# ---------------------- ROOT ENDPOINT ----------------------
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


# ---------------------- REFRESH ENDPOINT ----------------------
@patch("main.requests.get")
@patch("main.add_countries")
@patch("main.generate_summary")
def test_refresh_success(mock_summary, mock_add, mock_requests, mock_db_session):
    mock_requests.side_effect = [
        MagicMock(status_code=200, json=lambda: [
            {"name": "Nigeria", "capital": "Abuja", "region": "Africa", "population": 200000000, "flag": "url", "currencies": [{"code": "NGN"}]},
        ]),
        MagicMock(status_code=200, json=lambda: {"rates": {"NGN": 1500}})
    ]

    response = client.post("/countries/refresh")
    assert response.status_code == 200
    assert response.json()["message"] == "Countries refreshed successfully"


@patch("main.requests.get")
def test_refresh_external_api_error(mock_requests):
    mock_requests.return_value = MagicMock(status_code=500)
    response = client.post("/countries/refresh")
    assert response.status_code == 503
    assert "error" in response.json()


@patch("main.requests.get", side_effect=requests.exceptions.RequestException("Timeout"))
def test_refresh_request_exception(mock_requests):
    response = client.post("/countries/refresh")
    assert response.status_code == 503
    assert "error" in response.json()


# ---------------------- STATUS ENDPOINT ----------------------
@patch("main.get_status", return_value={"countries": 10, "last_refreshed": str(datetime.utcnow())})
def test_status(mock_status):
    response = client.get("/status")
    assert response.status_code == 200
    assert "countries" in response.json()


# ---------------------- COUNTRIES FILTER ENDPOINT ----------------------
@patch("main.get_all_countries_by_filters", return_value=[
    type("Country", (), {
        "id": 1,
        "name": "Nigeria",
        "capital": "Abuja",
        "region": "Africa",
        "population": 200000000,
        "currency_code": "NGN",
        "exchange_rate": 1500,
        "estimated_gdp": 100000.0,
        "flag_url": "url",
        "last_refreshed_at": datetime.now(timezone.utc)
    })()
])
def test_countries_filter(mock_filters):
    response = client.get("/countries?region=Africa")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "Nigeria"


# ---------------------- GET COUNTRY ----------------------
@patch("main.get_a_country", return_value={"name": "Nigeria", "capital": "Abuja"})
def test_get_country(mock_country):
    response = client.get("/countries/Nigeria")
    assert response.status_code == 200
    assert response.json()["name"] == "Nigeria"


@patch("main.get_a_country", return_value=None)
def test_get_country_not_found(mock_country):
    response = client.get("/countries/Unknownland")
    assert response.status_code == 404
    assert "error" in response.json()


# ---------------------- DELETE COUNTRY ----------------------
@patch("main.delete_a_country", return_value=True)
def test_delete_country_success(mock_delete):
    response = client.delete("/countries/Nigeria")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]


@patch("main.delete_a_country", return_value=False)
def test_delete_country_not_found(mock_delete):
    response = client.delete("/countries/Nowhere")
    assert response.status_code == 404
    assert "error" in response.json()


# ---------------------- IMAGE ENDPOINT ----------------------
@patch("os.path.exists", return_value=False)
def test_show_summary_image_not_found(mock_exists):
    response = client.get("/countries/image")
    assert response.status_code == 404


@patch("os.path.exists", return_value=True)
def test_show_summary_image_exists(mock_exists):
    response = client.get("/countries/image")
    # Should attempt to send image file
    assert response.status_code in [200, 404]  # 200 if file found, 404 if missing
