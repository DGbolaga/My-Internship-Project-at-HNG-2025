# String Analyzer Service API

This is a **RESTful API service** built with **FastAPI** and **SQLModel** that analyzes input strings, computes their properties, and stores them persistently in a database.

---

## 🚀 Live Demo

[View Deployed API on Railway](https://my-internship-project-at-hng-2025-production-3aae.up.railway.app/)  
*(Deployed using Railway with PostgreSQL configuration)*

---

## 🌟 Features Implemented

1. **String Analysis & Storage:**  
   Computes and stores the following properties for each string:
   - `length`
   - `is_palindrome` (case-insensitive)
   - `unique_characters`
   - `word_count`
   - `sha256_hash`
   - `character_frequency_map`

2. **CRUD Operations:**  
   - `POST /strings` → Analyze and store a string  
   - `GET /strings/{string_value}` → Retrieve analysis for a specific string  
   - `GET /strings` → Retrieve multiple strings with structured filters  
   - `GET /strings/filter-by-natural-language` → Retrieve using natural language queries  
   - `DELETE /strings/{string_value}` → Remove a string

3. **Filtering Options:**  
   - By `min_length`, `max_length`, `is_palindrome`, `word_count`, or `contains_character`
   - Natural language queries like *"all single word palindromic strings"* or *"strings longer than 10 characters"*

4. **Persistence:**  
   Uses **SQLite** for local development and **PostgreSQL** in production (via `DATABASE_URL`).

---

## 🛠️ Technology Stack

- **Backend Framework:** FastAPI  
- **ORM:** SQLModel (built on SQLAlchemy + Pydantic)  
- **Database:** PostgreSQL (Production) / SQLite (Local)  
- **Environment Management:** python-dotenv  
- **Server:** Uvicorn  
- **Testing:** Pytest  
- **Deployment:** Railway  

---

## 📦 Setup and Installation

### 🧩 Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- A **PostgreSQL** database instance (if deploying or testing with Postgres)

---

### ⚙️ 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPO_LINK>
cd Stage-1
```

---

### 🧰 2. Create and Activate a Virtual Environment

Create a .env file in the project root with:

```bash
DATABASE_URL=postgresql+psycopg2://<username>:<password>@<host>:<port>/<database>
```

---

### 📦 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

---

### 🔑 4. Environment Variables

Create a .env file in the project root with:
```bash
DATABASE_URL=postgresql+psycopg2://<username>:<password>@<host>:<port>/<database>
If omitted, the app defaults to sqlite:///database.db.

```

---



If omitted, the app defaults to sqlite:///database.db.

▶️ 5. Run the Application
```bash
uvicorn main:app --reload
```



The API will be available at:
👉 http://127.0.0.1:8000

You can test interactively via Swagger UI:
👉 http://127.0.0.1:8000/docs

---

🧪 Running Tests

Run the test suite with:
```bash
pytest -v
```

This ensures all endpoints and computations (string analysis, filters, and natural language queries) behave correctly.

---

📁 Project Structure
```bash

Stage-1/
├── main.py                      # FastAPI application entry point
├── test_main.py                 # Test cases using pytest
├── requirements.txt             # Dependencies
├── Procfile                     # Railway deployment config
├── README.md                    # Documentation
├── database.db                  # SQLite database (for local)
├── utilities/
│   ├── operations.py            # String analysis utility functions
│   ├── models.py                # Request/response models
│   ├── natural_language_parser.py # Converts natural text to filters
│   └── __init__.py
└── venv/                        # Virtual environment (excluded from Git)
```

---

🌐 API Endpoints Summary
Method	Endpoint	Description
POST	/strings	Analyze and store a new string
GET	/strings/{string_value}	Retrieve analysis of a specific string
GET	/strings	Retrieve all strings with structured filters
GET	/strings/filter-by-natural-language	Retrieve strings using human-readable queries
DELETE	/strings/{string_value}	Delete a string from the database

---

🧩 Example Natural Language Queries
Query	Parsed Filters
"all single word palindromic strings"	word_count=1, is_palindrome=True
"strings longer than 10 characters"	min_length=11
"strings containing the letter z"	contains_character=z
🚀 Deployment

This project is deployed on Railway with a PostgreSQL add-on.

To deploy your own version:

Push your repo to GitHub.

Create a new Railway project and connect your GitHub repo.

Add DATABASE_URL as an environment variable.

Deploy: Railway automatically runs the Procfile command.

---

👨‍💻 Author

Omogbolaga Daramola
Backend Dev @ HNG Internship 2025
📧 Email: [gbolagadaramola765@gmail.com](mailto:gbolagadaramola765@gmail.com)  
🔗 GitHub: [DGbolaga](https://github.com/DGbolaga)
