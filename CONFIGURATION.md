# Configuration Guide

## Environment Setup

The platform uses environment variables for configuration. 

### Files Provided

- **`.env.example`**: Template file with all available configuration options
- **`README.md`**: Complete documentation including setup instructions

### Quick Setup

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials where needed

### Required Configuration

#### Database
The platform uses SQLite by default (no setup required):
```
DATABASE_URL=sqlite:///./data/trading_platform.db
```

For PostgreSQL, update with your connection string.

#### Optional API Keys

The platform works without API keys but has limited functionality:

- **ALPHA_VANTAGE_API_KEY**: For additional market data sources
- **SERPAPI_KEY**: For enhanced web search (not required - DuckDuckGo works by default)

### Note on Security

Both `.env.example` and `README.md` contain ONLY field names with empty values.
No actual credentials are stored in the repository.

These files are provided in your workspace for reference and use.
