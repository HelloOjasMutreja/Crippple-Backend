# Crippple Backend - Apparel Marketplace API

A Django-based backend service that aggregates apparel search results from multiple e-commerce platforms including Google Shopping, Amazon India, Myntra, and Adidas.

## Features

- **Unified Search**: Search across multiple platforms with a single API call
- **Multi-platform Scraping**: Scrapes products from:
  - Google Shopping
  - Amazon India
  - Myntra
  - Adidas India
- **Concurrent Scraping**: Uses ThreadPoolExecutor for fast parallel scraping
- **Flexible Response Formats**: Choose between flat (deduplicated) or grouped (by platform) results
- **REST API**: RESTful API endpoints with JSON responses

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL (or use SQLite for development)
- Playwright browsers

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Crippple-Backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
playwright install-deps chromium
```

5. Create a `.env` file with your database credentials:
```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Start the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Search Apparel

Search for apparel products across multiple platforms.

**Endpoint:** `GET /api/search/`

**Query Parameters:**
- `q` (required): Search query (e.g., "hoodie", "jeans", "sneakers")
- `max_per_platform` (optional): Maximum results per platform (default: 20)
- `format` (optional): Response format - `flat` or `grouped` (default: `flat`)

**Example Requests:**

```bash
# Basic search - returns flat deduplicated list
curl "http://localhost:8000/api/search/?q=hoodie"

# Search with custom max results per platform
curl "http://localhost:8000/api/search/?q=sneakers&max_per_platform=10"

# Search with grouped format (results grouped by platform)
curl "http://localhost:8000/api/search/?q=jeans&format=grouped"
```

**Response Format (flat):**
```json
{
  "query": "hoodie",
  "count": 45,
  "results": [
    {
      "title": "Nike Sportswear Club Fleece Hoodie",
      "price": "₹3,495",
      "vendor": "Amazon India",
      "link": "https://www.amazon.in/...",
      "image": "https://...",
      "source": "amazon",
      "brand": "Nike"
    },
    ...
  ],
  "errors": []
}
```

**Response Format (grouped):**
```json
{
  "query": "hoodie",
  "total_results": 45,
  "platforms": {
    "google_shopping": {
      "count": 15,
      "results": [...]
    },
    "amazon": {
      "count": 12,
      "results": [...]
    },
    "myntra": {
      "count": 10,
      "results": [...]
    },
    "adidas": {
      "count": 8,
      "results": [...]
    }
  },
  "errors": []
}
```

### Legacy Google Shopping Search

Legacy endpoint for backward compatibility.

**Endpoint:** `GET /api/google-shopping/`

**Query Parameters:**
- `q` (required): Search query

**Example:**
```bash
curl "http://localhost:8000/api/google-shopping/?q=hoodie"
```

## Development

### Running Tests

```bash
python manage.py test
```

### Management Commands

#### Scrape Google Shopping
```bash
python manage.py scrape_google_shopping "hoodie" --max 20
```

## Architecture

### Scrapers

Each scraper is implemented as a standalone module in the `scrapers/` directory:

- `google_shopping_scraper.py`: Scrapes Google Shopping results
- `amazon_scraper.py`: Scrapes Amazon India
- `myntra_scraper.py`: Scrapes Myntra
- `adidas_scraper.py`: Scrapes Adidas India
- `unified_scraper.py`: Orchestrates all scrapers concurrently

All scrapers use **Playwright** for web scraping, which provides:
- JavaScript rendering
- Headless browser automation
- Stealth mode to avoid detection

### API Layer

The API is built with:
- **Django**: Web framework
- **Django REST Framework**: RESTful API functionality
- **CORS Headers**: Cross-origin resource sharing support

### Key Components

1. **Views** (`products/views.py`): Handles API requests and responses
2. **Unified Scraper** (`scrapers/unified_scraper.py`): Aggregates results from all platforms
3. **Individual Scrapers**: Platform-specific scraping logic
4. **Models** (`products/models.py`): Product data model (for future persistence)

## Configuration

### Settings

Key settings in `crippple_backend/settings.py`:

- `ALLOWED_HOSTS`: Configure allowed hosts for production
- `CORS_ALLOW_ALL_ORIGINS`: Set to `False` in production and configure specific origins
- `DEBUG`: Set to `False` in production

## Troubleshooting

### Environment Check

Run the environment checker to verify your setup:

```bash
python check_environment.py
```

This will check:
- Python version
- Required packages
- Playwright browser installation
- Django configuration
- Scraper modules

### Playwright Installation Issues

If you encounter issues installing Playwright browsers:

```bash
# Install system dependencies
playwright install-deps chromium

# Install browser
playwright install chromium
```

### Scraping Errors

If scrapers fail:
1. Check that Playwright browsers are installed
2. Verify internet connectivity
3. Check if website selectors need updating (websites change their HTML structure)
4. Review error logs for specific platform issues

**See [SCRAPING_FIXES.md](SCRAPING_FIXES.md) for detailed information about recent fixes for:**
- Myntra HTTP/2 protocol errors
- Adidas timeout issues
- Google Shopping stale selectors
- General anti-scraping improvements

### Database Connection Issues

For development, you can use SQLite instead of PostgreSQL by modifying `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Add your license information here]

## Contact

[Add contact information here]
