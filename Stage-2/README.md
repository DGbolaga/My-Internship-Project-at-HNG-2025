# HNG Internship (Stage-2):  Country Currency & Exchange API

A RESTful API that fetches country data from external APIs, stores it in a database, and provides CRUD operations with exchange rate calculations.

---

## 🚀 Features

* Fetch country data from **restcountries.com**
* Fetch currency exchange rates from **open.er-api.com**
* Compute **estimated GDP** for each country
* Filter and sort countries by region, currency, GDP, population, or name
* Generate and serve **summary images** of top-performing countries
* Perform full **CRUD** operations on country data
* Unit-tested endpoints with **pytest**

---

## 🧠 Tech Stack

| Component        | Technology                      |
| ---------------- | ------------------------------- |
| Framework        | **FastAPI**                     |
| ORM              | **SQLAlchemy**                  |
| Database         | **PostgreSQL / SQLite (local)** |
| Environment      | **python-dotenv**               |
| Image Generation | **Pillow**, **CairoSVG**        |
| HTTP Client      | **Requests**                    |
| Testing          | **Pytest**                      |

---

## 📁 Project Structure

```
Stage-2-demo/
├── .env.example         # example of environment variables
├── main.py              # FastAPI app & API routes
├── crud.py              # Database operations
├── db.py                # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── test_main.py         # Test cases for all endpoints
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── cache/               # Stores generated summary images
├── venv/                # Virtual environment
└── __pycache__/         # Auto-generated cache files
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd Stage-2-demo
```

### 2️⃣ Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # (Windows: venv\Scripts\activate)
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```bash
DATABASE_URL=sqlite:///./countries.db
COUNTRIES_API=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_RATES_API=https://open.er-api.com/v6/latest/USD
```

*(PostgreSQL users can replace the `DATABASE_URL` accordingly.)*

### 5️⃣ Run the Application

```bash
uvicorn main:app --reload
```

### 6️⃣ Access the API

* Root: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🌐 API Endpoints

### 🌀 Root

```
GET /
```

Returns a welcome message and link to docs.

---

### 🔁 Refresh Countries

```
POST /countries/refresh
```

Fetches countries and exchange rates, calculates estimated GDPs, updates database, and regenerates the summary image.

---

### 📊 Get Status

```
GET /status
```

Returns the total number of countries and the last refresh timestamp.

---

### 🌎 Get All Countries

```
GET /countries
GET /countries?region=Africa
GET /countries?currency=USD
GET /countries?sort=gdp_desc
```

Retrieves countries with optional filters and sorting.

**Supported Sorts:**
`gdp_desc`, `gdp_asc`, `name_asc`, `name_desc`, `population_desc`, `population_asc`

---

### 🔍 Get Single Country

```
GET /countries/{name}
```

Fetch a country’s details by name.

---

### ❌ Delete Country

```
DELETE /countries/{name}
```

Deletes a country by name from the database.

---

### 🖼️ Get Summary Image

```
GET /countries/image
```

Returns a generated summary image showing top 5 countries by GDP.

---

## 🧪 Testing

Run tests with:

```bash
pytest -v
```

Example:

```bash
pytest test_main.py -v
```

---

## 🧩 Example Responses

### ✅ `GET /status`

```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-27T10:15:00Z"
}
```

### ✅ `GET /countries?region=Africa`

```json
[
  {
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": 1500.23,
    "estimated_gdp": 27485250000.0,
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-27T10:15:00Z"
  }
]
```

---

## ⚠️ Error Handling

| Status | Description                        |
| ------ | ---------------------------------- |
| `400`  | Validation failed                  |
| `404`  | Country not found or image missing |
| `503`  | External API unavailable           |

**Example:**

```json
{
  "error": "Country not found"
}
```

---

## 📸 Summary Image Example

When `/countries/refresh` runs successfully, a file `cache/summary.png` is created showing:

* Total countries count
* Last refresh timestamp
* Top 5 countries by GDP with their flags

---

## ☁️ Deployment (Railway Example)

1. Push your project to GitHub
2. Go to [Railway.app](https://railway.app) → “New Project” → “Deploy from GitHub”
3. Connect your repo
4. Add environment variables

   * `DATABASE_URL`
5. Railway will auto-build and deploy your FastAPI app
6. Access via your generated public URL, e.g.:

   ```
   https://country-currency-api.up.railway.app
   ```

---

## 🧾 License

MIT License © 2025 — Developed by **Omogbolaga Daramola**
For HNG Internship (Stage-2)

