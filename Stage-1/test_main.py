import pytest
from fastapi.testclient import TestClient
from main import app, create_db_and_tables
import os

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Clean previous DB if exists
    if os.path.exists("database.db"):
        os.remove("database.db")
    create_db_and_tables()

# Add a case-insensitive palindrome test
def test_create_case_insensitive_palindrome():
    payload = {"value": "Racecar"}
    response = client.post("/strings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == "Racecar"
    # This should now be TRUE due to the fix in operations.py
    assert data["properties"]["is_palindrome"] is True 


def test_create_string():
    payload = {"value": "madam"}
    response = client.post("/strings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == "madam"
    assert data["properties"]["is_palindrome"] is True
    assert "sha256_hash" in data["properties"]


def test_create_string_conflict():
    payload = {"value": "madam"}
    response = client.post("/strings", json=payload)
    assert response.status_code == 409  # already exists


def test_get_specific_string():
    response = client.get("/strings/madam")
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "madam"
    assert data["properties"]["is_palindrome"] is True


def test_get_string_by_filter_palindrome():
    response = client.get("/strings?is_palindrome=true")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    # Ensure both "madam" and "Racecar" are found
    assert len(data["data"]) >= 2
    assert all(item["properties"]["is_palindrome"] for item in data["data"])


def test_get_string_by_filter_length_range():
    response = client.get("/strings?min_length=3&max_length=10")
    assert response.status_code == 200
    data = response.json()
    for item in data["data"]:
        assert 3 <= item["properties"]["length"] <= 10


def test_filter_by_natural_language_palindrome():
    response = client.get("/strings/filter-by-natural-language?query=all single word palindromic strings")
    assert response.status_code == 200
    data = response.json()
    assert "interpreted_query" in data
    assert data["interpreted_query"]["parsed_filters"]["is_palindrome"] is True
    assert data["interpreted_query"]["parsed_filters"]["word_count"] == 1


def test_filter_by_natural_language_contains_letter():
    response = client.get("/strings/filter-by-natural-language?query=strings containing the letter m")
    assert response.status_code == 200
    data = response.json()
    filters = data["interpreted_query"]["parsed_filters"]
    assert filters.get("contains_character") == "m"

# The following deletion tests will use "Racecar" and "madam"
def test_delete_first_string():
    response = client.delete("/strings/madam")
    assert response.status_code == 204


def test_delete_second_string():
    response = client.delete("/strings/Racecar")
    assert response.status_code == 204


def test_delete_non_existent_string():
    response = client.delete("/strings/doesnotexist")
    assert response.status_code == 404


def test_get_deleted_string():
    response = client.get("/strings/madam")
    assert response.status_code == 404