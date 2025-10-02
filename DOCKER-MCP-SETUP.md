# Docker MCP Catalog Setup for YFinance

This guide shows how to use the yfinance MCP server with Docker MCP Gateway's custom catalog feature.

## Setup Steps

### 1. Ensure Docker Image is Built

```bash
cd /home/misza/dev/yfinance
docker-compose up -d --build
docker tag yfinance_yfinance-mcp:latest yfinance-mcp:latest
```

### 2. Create Custom Catalog

The catalog has already been created and configured:

```bash
# List existing catalogs
docker mcp catalog ls

# View yfinance catalog
docker mcp catalog show yfinance-catalog
```

Output should show:
```
yfinance: Yahoo Finance MCP server providing comprehensive market data access with 20 tools...
```

### 3. Run Gateway with YFinance

**Option A: Use Additional Catalog (Recommended)**

This adds yfinance to the default Docker catalog:

```bash
docker mcp gateway run \
  --additional-catalog yfinance-catalog.yaml \
  --servers yfinance \
  --transport sse \
  --port 8812
```

**Option B: Use Only YFinance Catalog**

```bash
docker mcp gateway run \
  --catalog yfinance-catalog.yaml \
  --servers yfinance \
  --transport sse \
  --port 8812
```

**Option C: Enable All Servers (yfinance + Docker official)**

```bash
docker mcp gateway run \
  --additional-catalog yfinance-catalog.yaml \
  --enable-all-servers \
  --transport sse \
  --port 8812
```

### 4. Test Connection

Once the gateway is running, test it:

```bash
# Via HTTP
curl http://localhost:8812/

# Via SSE (Server-Sent Events)
curl -N -H "Accept: text/event-stream" http://localhost:8812/sse
```

### 5. Connect Claude Code

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "yfinance-gateway": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "http://localhost:8812/sse",
        "-H", "Content-Type: application/json"
      ]
    }
  }
}
```

Or use with the stdio transport directly:

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

## Catalog Files

The yfinance catalog is stored at:
- **Local file**: `~/.docker/mcp/catalogs/yfinance-catalog.yaml`
- **Source file**: `/home/misza/dev/yfinance/yfinance-mcp-catalog.yaml`

## Available Tools

The yfinance MCP server provides 20 tools:

**Basic Data (6):**
- get_ticker_info
- get_ticker_history
- get_ticker_financials
- get_ticker_recommendations
- download_multiple
- search_tickers

**Corporate Actions (4):**
- get_ticker_dividends
- get_ticker_splits
- get_ticker_actions
- get_ticker_capital_gains

**Earnings & Analysis (3):**
- get_ticker_earnings
- get_ticker_earnings_dates
- get_ticker_analyst_price_targets

**Ownership (3):**
- get_ticker_institutional_holders
- get_ticker_major_holders
- get_ticker_insider_transactions

**Market Data (3):**
- get_ticker_news
- get_ticker_options
- get_ticker_option_chain

**Other (1):**
- get_ticker_isin

## Troubleshooting

### Port Already in Use

If port 8812 is in use, change to another port:

```bash
docker mcp gateway run \
  --additional-catalog yfinance-catalog.yaml \
  --servers yfinance \
  --transport sse \
  --port 8813
```

### Can't List Tools Error

If you see "Can't list tools yfinance: invalid request", ensure:

1. Docker image is built and tagged correctly:
   ```bash
   docker images | grep yfinance-mcp
   ```

2. Container can be started manually:
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
     docker run -i --rm yfinance-mcp:latest
   ```

### Update Catalog

To update the catalog after making changes:

```bash
# Export current catalog
docker mcp catalog export yfinance-catalog ./yfinance-backup.yaml

# Update the source file
# Then re-add the server
docker mcp catalog add yfinance-catalog yfinance ./yfinance-mcp-catalog.yaml --force
```

## Export and Share

Export the catalog to share with others:

```bash
docker mcp catalog export yfinance-catalog ./yfinance-mcp-catalog-export.yaml
```

Others can import it:

```bash
docker mcp catalog import ./yfinance-mcp-catalog-export.yaml
```
