# HNG Internship (Stage-2):  Country Currency & Exchange API

A RESTful API that fetches country data from external APIs, stores it in a database, and provides CRUD operations with exchange rate calculations.

## Features

- Fetch country data from restcountries.com
- Get exchange rates from open.er-api.com
- Calculate estimated GDP for each country
- Filter countries by region and currency
- Sort countries by GDP, population, or name
- Generate summary images with top countries
- Full CRUD operations

## Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database (easy to deploy, no setup required)
- **Pillow** - Image generation
- **Pytest** - Testing

## Project Structure

```
country-currency-api/
├── main.py              # FastAPI app & endpoints
├── models.py            # Database models
├── database.py          # Database configuration
├── crud.py              # Database operations
├── test_api.py          # Test suite
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── README.md           # This file
└── cache/              # Generated images (auto-created)
```

## Setup Instructions

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd country-currency-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file (optional)**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` if you want to customize settings (default SQLite works fine)

5. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Refresh Countries
```bash
POST /countries/refresh
```
Fetches all countries and exchange rates, then caches them in the database.

### Get All Countries
```bash
GET /countries
GET /countries?region=Africa
GET /countries?currency=NGN
GET /countries?sort=gdp_desc
```
Returns all countries with optional filters and sorting.

**Sort options:** `gdp_desc`, `gdp_asc`, `name_asc`, `name_desc`, `population_desc`, `population_asc`

### Get Single Country
```bash
GET /countries/{name}
```
Returns a specific country by name.

### Delete Country
```bash
DELETE /countries/{name}
```
Deletes a country record.

### Get Status
```bash
GET /status
```
Returns total countries and last refresh timestamp.

### Get Summary Image
```bash
GET /countries/image
```
Returns a generated PNG image with summary statistics.

## Testing

Run all tests:
```bash
pytest test_api.py -v
```

Run tests manually:
```bash
python test_api.py
```

## Deployment on Railway

1. **Create a new project on Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"

2. **Connect your repository**
   - Authorize Railway to access your GitHub
   - Select your repository

3. **Configure the deployment**
   - Railway will auto-detect Python
   - No additional configuration needed (SQLite database is file-based)

4. **Environment Variables (optional)**
   - `PORT` - Railway sets this automatically
   - `DATABASE_URL` - Defaults to SQLite, no need to change

5. **Deploy**
   - Railway will automatically build and deploy
   - You'll get a public URL like `https://your-app.railway.app`

## Environment Variables

Create a `.env` file for local development:

```env
DATABASE_URL=sqlite:///./countries.db
PORT=8000
```

**Note:** For Railway deployment, these are optional. The app uses sensible defaults.

## Sample Response

### GET /countries?region=Africa

```json
[
  {
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": 1600.23,
    "estimated_gdp": 25767448125.2,
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-22T18:00:00Z"
  }
]
```

### GET /status

```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-22T18:00:00Z"
}
```

## Error Handling

The API returns consistent JSON error responses:

- `400` - Validation failed
- `404` - Country not found
- `500` - Internal server error
- `503` - External API unavailable

Example error response:
```json
{
  "error": "Country not found"
}
```

## How It Works

1. **Data Fetching** - The `/countries/refresh` endpoint fetches data from two external APIs
2. **Currency Matching** - Each country's currency is matched with its exchange rate
3. **GDP Calculation** - Estimated GDP = population × random(1000-2000) ÷ exchange_rate
4. **Database Storage** - Data is stored/updated in SQLite with case-insensitive name matching
5. **Image Generation** - A summary image is created showing top 5 countries by GDP

## Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - Database ORM
- `requests` - HTTP client for external APIs
- `pillow` - Image processing
- `pytest` - Testing framework
- `httpx` - Test client
- `python-dotenv` - Environment variables

## Notes

- The database file `countries.db` is created automatically on first run
- Images are saved in the `cache/` directory (created automatically)
- Exchange rates are fetched in USD base currency
- Countries with no currency data are still stored (with null values)
- The random GDP multiplier is recalculated on each refresh

## Troubleshooting

**Database locked error:**
- This can happen with SQLite if multiple processes access it. Just retry the request.

**External API timeout:**
- The APIs have a 10-second timeout. If they fail, you'll get a 503 error.

**Image generation fails:**
- The app tries to use system fonts but falls back to default if unavailable.

## License

MIT License - feel free to use this project however you like!

