# Installation Guide

## Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd trading-platform

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install chromium

# 5. Initialize database
python scripts/init_db.py

# 6. Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# 7. Run example to test
python scripts/test_example.py
```

## Running the Platform

### Option 1: Run Locally

```bash
# Terminal 1 - API Server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Dashboard
streamlit run src/dashboard/app.py

# Terminal 3 - Scheduler (optional)
python -m src.scheduler.main
```

### Option 2: Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Accessing the Platform

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501

## Next Steps

1. Configure API keys in `.env` (optional but recommended)
2. Run the example script to populate sample data
3. Explore the dashboard to see strategies and backtests
4. Use the API to create custom strategies
5. Start the scheduler for automated scraping

## Troubleshooting

### Dependencies Not Installing
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Playwright Issues
```bash
playwright install-deps
playwright install chromium
```

### Database Errors
```bash
rm -rf data/*.db
python scripts/init_db.py
```

## Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt

# Setup pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run tests
pytest

# Format code
make format

# Lint code
make lint
```
