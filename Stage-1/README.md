# String Analyzer Service API

This is a **RESTful API service** built with FastAPI and SQLModel that analyzes input strings, computes their properties, and stores them persistently. 


## 🚀 Live Demo

[Deploy on Railway](#deployment) | [Test the API](https://my-internship-project-at-hng-2025-production-3aae.up.railway.app/)

## 🌟 Features Implemented

The service supports the following core functions:

1.  **Analysis & Storage:** Computes `length`, `is_palindrome` (case-insensitive), `unique_characters`, `word_count`, `sha256_hash`, and `character_frequency_map` for any submitted string.
2.  **CRUD Operations:** `POST` to create, `GET` to retrieve (by value or hash), and `DELETE` to remove.
3.  **Structured Filtering:** `GET /strings` supports filtering by multiple query parameters (e.g., `min_length`, `is_palindrome`).
4.  **Natural Language Filtering:** `GET /strings/filter-by-natural-language` allows for filtering using human-readable queries.
5.  **Persistence:** Uses SQLite for local development and is configured for **PostgreSQL** in a production environment via a `DATABASE_URL` environment variable.

## 🛠️ Technology Stack

* **API Framework:** FastAPI
* **ORM:** SQLModel (SQLAlchemy + Pydantic)
* **Database:** PostgreSQL (Recommended for Production), SQLite (Default for Local)
* **Dependencies:** `uvicorn`, `python-dotenv`, `psycopg2-binary` (PostgreSQL driver)
* **Testing:** `pytest`

## 📦 Setup and Installation

### Prerequisites

* **Python 3.10+** (or any modern version)
* A package manager (e.g., `pip`)
* A running PostgreSQL instance (for production deployment or if you choose to use it locally)

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPO_LINK>
cd Stage-1