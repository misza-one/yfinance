# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**yfinance** is a Python library for downloading market data from Yahoo! Finance's API. It provides a Pythonic interface for fetching financial and market data for stocks, ETFs, funds, and other securities.

**Important**: This project is not affiliated with Yahoo, Inc. The library uses Yahoo's publicly available APIs for research and educational purposes. Always refer to Yahoo!'s terms of use.

## Branch Model

- **dev**: New features and most bug fixes are merged here for testing
- **main**: Stable branch where PyPI releases are created

Pull requests should target the `dev` branch.

## Development Commands

### Install Development Environment

```bash
# Install package in editable mode
pip install -e .

# For contributing, install from specific branch
pip install git+https://github.com/ranaroussi/yfinance.git@dev
```

### Running Tests

```bash
# Run all tests
pytest --cov=yfinance/

# Run specific test file
pytest tests/test_ticker.py

# Run with coverage
pytest --cov=yfinance/ --cov-report=html
```

### Building Documentation

Documentation is auto-generated from code at https://ranaroussi.github.io/yfinance

See https://ranaroussi.github.io/yfinance/development/documentation.html for local docs setup.

### Package Installation

```bash
# Install from PyPI
pip install yfinance

# Install from local source
pip install -e .
```

## Architecture Overview

### Core Components

The library is structured around these main public APIs:

- **`Ticker`** (`yfinance/ticker.py`): Single ticker data access - the primary interface for fetching data about individual securities
- **`Tickers`** (`yfinance/tickers.py`): Multi-ticker wrapper for batch operations
- **`download()`** (`yfinance/multi.py`): Efficient multi-ticker historical data download
- **`Search`** (`yfinance/search.py`): Search for tickers by company name or symbol
- **`Lookup`** (`yfinance/lookup.py`): Alternative ticker lookup functionality
- **`Market`** (`yfinance/domain/market.py`): Market-level information
- **`Sector`** / **`Industry`** (`yfinance/domain/`): Sector and industry data
- **`WebSocket`** / **`AsyncWebSocket`** (`yfinance/live.py`): Real-time streaming data
- **`Screener`** / **`EquityQuery`** / **`FundQuery`** (`yfinance/screener/`): Screen markets with custom queries

### Key Internal Architecture

**Data Fetching Layer** (`yfinance/base.py`, `yfinance/data.py`):
- `TickerBase`: Base class providing common functionality for all ticker objects
- `YfData`: Centralized data fetching with request caching, rate limiting, and session management
- Uses `requests_cache` for intelligent caching and `requests_ratelimiter` for API throttling

**Scrapers** (`yfinance/scrapers/`):
- Modular data extraction separated by data type:
  - `history.py`: Price history and OHLCV data
  - `fundamentals.py`: Financial statements (income, balance sheet, cash flow)
  - `analysis.py`: Analyst recommendations and estimates
  - `quote.py`: Real-time quote data
  - `holders.py`: Institutional and insider ownership
  - `funds.py`: Mutual fund specific data

**Data Processing** (`yfinance/utils.py`):
- DataFrame manipulation and timezone handling
- Price repair algorithms for stock splits and dividends
- Error handling and data validation

**Caching** (`yfinance/cache.py`):
- Timezone cache using `peewee` ORM with SQLite
- Request caching via `requests_cache`

**WebSocket/Live Data** (`yfinance/live.py`):
- Protobuf-based real-time data streaming
- Both synchronous (`WebSocket`) and asynchronous (`AsyncWebSocket`) implementations

### Data Flow

1. User calls `Ticker("AAPL").info` or similar method
2. `Ticker` inherits from `TickerBase`, which uses `YfData` for HTTP requests
3. `YfData` checks cache, applies rate limiting, fetches from Yahoo Finance API
4. Appropriate scraper module parses JSON/HTML response
5. Data is transformed into pandas DataFrames or Python dicts
6. Results cached for subsequent requests

## MCP Server (Custom Addition)

This repository includes a custom Model Context Protocol (MCP) server for exposing yfinance data via Docker:

### MCP Files

- **`mcp_stdio_server.py`**: stdio-based MCP server (20 tools) - used by Docker
- **`mcp_server.py`**: FastAPI-based HTTP MCP server (for development)
- **`Dockerfile`**: Container with Python 3.11-slim, yfinance, and dependencies
- **`docker-compose.yml`**: Service configuration for yfinance-mcp-server
- **`requirements-mcp.txt`**: Additional MCP server dependencies (FastAPI, uvicorn)

### MCP Server Tools (20 total)

The MCP server exposes all major yfinance capabilities:

**Basic Data (6):**
- get_ticker_info, get_ticker_history, get_ticker_financials
- get_ticker_recommendations, download_multiple, search_tickers

**Corporate Actions (4):**
- get_ticker_dividends, get_ticker_splits, get_ticker_actions, get_ticker_capital_gains

**Earnings & Analysis (3):**
- get_ticker_earnings, get_ticker_earnings_dates, get_ticker_analyst_price_targets

**Ownership (3):**
- get_ticker_institutional_holders, get_ticker_major_holders, get_ticker_insider_transactions

**Market Data (3):**
- get_ticker_news, get_ticker_options, get_ticker_option_chain

**Other (1):**
- get_ticker_isin

### Running MCP Server

```bash
# Build and start with docker-compose
docker-compose up -d --build

# Tag image for MCP client compatibility
docker tag yfinance_yfinance-mcp:latest yfinance-mcp:latest

# Test via stdio
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  docker run -i --rm yfinance-mcp:latest

# Stop server
docker-compose down
```

### MCP Configuration

Claude Code connects via `.mcp.json`:
```json
{
  "mcpServers": {
    "yfinance": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--init", "yfinance-mcp:latest"]
    }
  }
}
```

After rebuilding the Docker image, always run:
```bash
docker tag yfinance_yfinance-mcp:latest yfinance-mcp:latest
```

## Common Patterns

### Ticker Data Access

All ticker data is lazily loaded - data is only fetched when accessed:

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")
ticker.info              # Company info (dict)
ticker.history()         # Historical prices (DataFrame)
ticker.dividends         # Dividend history (Series)
ticker.splits            # Stock splits (Series)
ticker.financials        # Income statement (DataFrame)
ticker.balance_sheet     # Balance sheet (DataFrame)
ticker.cashflow          # Cash flow statement (DataFrame)
ticker.recommendations   # Analyst recommendations (DataFrame)
ticker.institutional_holders  # Institutional ownership (DataFrame)
ticker.option_chain()    # Options data (namedtuple of DataFrames)
```

### Bulk Downloads

Use `download()` for efficient multi-ticker fetching:

```python
import yfinance as yf

# Download multiple tickers at once
data = yf.download(["AAPL", "GOOGL", "MSFT"], period="1mo", interval="1d")
```

### WebSocket Streaming

```python
import yfinance as yf

# Synchronous
ws = yf.WebSocket(['AAPL', 'GOOGL'])
ws.start()

# Asynchronous
import asyncio
aws = yf.AsyncWebSocket(['AAPL'])
await aws.start()
```

## Important Notes

- **Yahoo API**: The library depends on Yahoo Finance's undocumented APIs, which can change without notice
- **Rate Limiting**: Built-in rate limiting prevents API blocks; avoid disabling unless necessary
- **Timezone Handling**: Market data includes timezone information; be careful with timezone-naive operations
- **Error Handling**: Network errors, missing data, and API changes should be handled gracefully
- **Caching**: Default caching improves performance but may return stale data; clear cache when needed

## Testing

Tests use `pytest` and are organized by functionality:
- `test_ticker.py`: Core Ticker functionality
- `test_prices.py`: Historical price data
- `test_price_repair.py`: Stock split/dividend adjustments
- `test_search.py`: Search functionality
- `test_screener.py`: Screener queries
- `test_cache.py`: Caching behavior

Mock external API calls in tests to avoid dependencies on Yahoo Finance availability.
