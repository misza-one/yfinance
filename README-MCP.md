# Yahoo Finance MCP Server

A Docker-based MCP (Model Context Protocol) server providing access to Yahoo Finance market data through a FastAPI interface.

## Features

- **Ticker Information**: Get comprehensive stock information including company details, financials, and statistics
- **Historical Data**: Retrieve OHLCV (Open, High, Low, Close, Volume) data for any period
- **Financial Statements**: Access income statements, balance sheets, and cash flow data
- **Analyst Recommendations**: Get analyst ratings and recommendations
- **Multi-Ticker Download**: Efficiently download data for multiple tickers at once
- **Search**: Search for stocks, ETFs, and other securities
- **Market/Sector/Industry Info**: Get information about markets, sectors, and industries

## Quick Start

### Build and Run with Docker Compose

```bash
# Build the Docker image
docker compose build

# Start the server (runs on port 8001)
docker compose up -d

# Check server health
curl http://localhost:8001/health

# View logs
docker logs yfinance-mcp-server

# Stop the server
docker compose down
```

### Using the MCP Server

The server runs on `http://localhost:8001` and provides the following endpoints:

#### Health Check
```bash
curl http://localhost:8001/health
```

#### List Available Tools
```bash
curl http://localhost:8001/mcp/tools
```

#### Get Ticker Information
```bash
curl -X POST http://localhost:8001/tools/ticker/info \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL"}'
```

#### Get Historical Price Data
```bash
curl -X POST http://localhost:8001/tools/ticker/history \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "period": "1mo",
    "interval": "1d"
  }'
```

#### Get Financial Statements
```bash
curl -X POST http://localhost:8001/tools/ticker/financials \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL"}'
```

#### Get Analyst Recommendations
```bash
curl -X POST http://localhost:8001/tools/ticker/recommendations \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL"}'
```

#### Download Multiple Tickers
```bash
curl -X POST http://localhost:8001/tools/download \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "GOOGL", "MSFT"],
    "period": "1mo",
    "interval": "1d"
  }'
```

#### Search for Tickers
```bash
curl -X POST http://localhost:8001/tools/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "apple",
    "max_results": 10
  }'
```

## API Documentation

Once the server is running, visit:
- Interactive API docs: http://localhost:8001/docs
- OpenAPI schema: http://localhost:8001/openapi.json

## Configuration

### Port Configuration

By default, the server runs on port 8001. To change the port, edit `docker-compose.yml`:

```yaml
environment:
  - PORT=8002
command: ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8002"]
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8002/health')"]
```

### Network Mode

The server uses `network_mode: host` to avoid DNS resolution issues. This means the container shares the host's network stack.

## Available Tools

| Tool Name | Description |
|-----------|-------------|
| `get_ticker_info` | Get comprehensive information about a stock ticker |
| `get_ticker_history` | Get historical price data for a ticker |
| `get_ticker_financials` | Get financial statements (income, balance sheet, cash flow) |
| `get_ticker_recommendations` | Get analyst recommendations for a ticker |
| `download_multiple` | Download data for multiple tickers efficiently |
| `search_tickers` | Search for stocks, ETFs, and other securities |

## Development

### File Structure

```
.
├── mcp_server.py           # FastAPI MCP server implementation
├── yfinance/               # yfinance package source
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # yfinance dependencies
└── requirements-mcp.txt    # Additional MCP server dependencies
```

### Local Development

```bash
# Install dependencies
pip install -r requirements-mcp.txt

# Run locally
uvicorn mcp_server:app --host 0.0.0.0 --port 8001 --reload
```

## Troubleshooting

### Port Already in Use

If port 8001 is already in use, either:
1. Stop the conflicting service
2. Change the port in `docker-compose.yml`

### DNS Resolution Issues

The Dockerfile uses `network: host` mode during build to avoid DNS resolution issues. If you still experience problems:

```bash
# Check Docker DNS settings
docker run --rm alpine ping -c 1 google.com

# Rebuild with no cache
docker compose build --no-cache
```

## License

This project uses the yfinance library, which is licensed under Apache 2.0.

**Note**: yfinance is not affiliated, endorsed, or vetted by Yahoo, Inc. Refer to Yahoo!'s terms of use for details on your rights to use the actual data downloaded.
