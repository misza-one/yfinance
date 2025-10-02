#!/usr/bin/env python3
"""
Yahoo Finance MCP Server - stdio implementation
Model Context Protocol server providing Yahoo Finance data
"""
import sys
import json
import logging
from typing import Any, Sequence
import yfinance as yf
import pandas as pd

# Configure logging to file only (not stderr to avoid interfering with stdio)
logging.basicConfig(
    level=logging.DEBUG,
    filename='/tmp/yfinance_mcp.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "get_ticker_info",
                "description": "Get comprehensive information about a stock ticker including company details, financials, and key statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol (e.g., AAPL, TSLA, GOOGL)"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_history",
                "description": "Get historical price data (OHLCV) for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        },
                        "period": {
                            "type": "string",
                            "description": "Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max",
                            "default": "1mo"
                        },
                        "interval": {
                            "type": "string",
                            "description": "Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo",
                            "default": "1d"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_financials",
                "description": "Get financial statements including income statement, balance sheet, and cash flow",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_recommendations",
                "description": "Get analyst recommendations and ratings for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol"
                        }
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "download_multiple",
                "description": "Download data for multiple tickers efficiently (bulk download)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ticker symbols"
                        },
                        "period": {
                            "type": "string",
                            "description": "Time period",
                            "default": "1mo"
                        },
                        "interval": {
                            "type": "string",
                            "description": "Data interval",
                            "default": "1d"
                        }
                    },
                    "required": ["symbols"]
                }
            },
            {
                "name": "search_tickers",
                "description": "Search for stocks, ETFs, and other securities by name or symbol",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (company name or ticker)"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_ticker_dividends",
                "description": "Get historical dividend payments for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_splits",
                "description": "Get stock split history for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_actions",
                "description": "Get all corporate actions (dividends + splits) for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_capital_gains",
                "description": "Get capital gains distributions for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_earnings",
                "description": "Get earnings data for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_earnings_dates",
                "description": "Get upcoming and past earnings dates/calendar for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"},
                        "limit": {"type": "integer", "default": 12, "description": "Number of earnings dates to return"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_analyst_price_targets",
                "description": "Get analyst price targets and consensus for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_institutional_holders",
                "description": "Get institutional ownership data for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_major_holders",
                "description": "Get major shareholders breakdown for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_insider_transactions",
                "description": "Get insider transaction data (smart money activity) for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_news",
                "description": "Get latest news articles for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"},
                        "max_items": {"type": "integer", "default": 10, "description": "Maximum number of news items"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_options",
                "description": "Get available options expiration dates for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            },
            {
                "name": "get_ticker_option_chain",
                "description": "Get full options chain (calls and puts) for a specific expiration date",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"},
                        "expiration_date": {"type": "string", "description": "Options expiration date (YYYY-MM-DD format)"}
                    },
                    "required": ["symbol", "expiration_date"]
                }
            },
            {
                "name": "get_ticker_isin",
                "description": "Get ISIN identifier for a ticker",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["symbol"]
                }
            }
        ]

    def df_to_dict(self, df):
        """Convert DataFrame to JSON-serializable dict"""
        if df is None or df.empty:
            return {}
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()
        return json.loads(df.to_json(orient='records', date_format='iso'))

    def handle_initialize(self, params: dict) -> dict:
        """Handle initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "yfinance",
                "version": "1.0.0"
            }
        }

    def handle_tools_list(self, params: dict) -> dict:
        """List available tools"""
        return {"tools": self.tools}

    def handle_tools_call(self, params: dict) -> dict:
        """Execute a tool call"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "get_ticker_info":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "info": ticker.info
                }

            elif tool_name == "get_ticker_history":
                ticker = yf.Ticker(arguments["symbol"])
                period = arguments.get("period", "1mo")
                interval = arguments.get("interval", "1d")
                hist = ticker.history(period=period, interval=interval)
                result = {
                    "symbol": arguments["symbol"],
                    "period": period,
                    "interval": interval,
                    "data": self.df_to_dict(hist)
                }

            elif tool_name == "get_ticker_financials":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "income_statement": self.df_to_dict(ticker.income_stmt),
                    "balance_sheet": self.df_to_dict(ticker.balance_sheet),
                    "cash_flow": self.df_to_dict(ticker.cashflow)
                }

            elif tool_name == "get_ticker_recommendations":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "recommendations": self.df_to_dict(ticker.recommendations)
                }

            elif tool_name == "download_multiple":
                data = yf.download(
                    tickers=" ".join(arguments["symbols"]),
                    period=arguments.get("period", "1mo"),
                    interval=arguments.get("interval", "1d"),
                    group_by=arguments.get("group_by", "column"),
                    threads=True
                )
                result = {
                    "symbols": arguments["symbols"],
                    "period": arguments.get("period", "1mo"),
                    "interval": arguments.get("interval", "1d"),
                    "data": self.df_to_dict(data)
                }

            elif tool_name == "search_tickers":
                search = yf.Search(arguments["query"])
                max_results = arguments.get("max_results", 10)
                results = search.quotes[:max_results]
                result = {
                    "query": arguments["query"],
                    "count": len(results),
                    "results": results
                }

            elif tool_name == "get_ticker_dividends":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "dividends": self.df_to_dict(ticker.dividends)
                }

            elif tool_name == "get_ticker_splits":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "splits": self.df_to_dict(ticker.splits)
                }

            elif tool_name == "get_ticker_actions":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "actions": self.df_to_dict(ticker.actions)
                }

            elif tool_name == "get_ticker_capital_gains":
                ticker = yf.Ticker(arguments["symbol"])
                capital_gains = ticker.capital_gains
                result = {
                    "symbol": arguments["symbol"],
                    "capital_gains": self.df_to_dict(capital_gains) if capital_gains is not None else []
                }

            elif tool_name == "get_ticker_earnings":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "earnings": self.df_to_dict(ticker.earnings)
                }

            elif tool_name == "get_ticker_earnings_dates":
                ticker = yf.Ticker(arguments["symbol"])
                earnings_dates = ticker.earnings_dates
                if earnings_dates is not None and not earnings_dates.empty:
                    limit = arguments.get("limit", 12)
                    earnings_dates = earnings_dates.head(limit)
                result = {
                    "symbol": arguments["symbol"],
                    "earnings_dates": self.df_to_dict(earnings_dates)
                }

            elif tool_name == "get_ticker_analyst_price_targets":
                ticker = yf.Ticker(arguments["symbol"])
                info = ticker.info
                price_targets = {
                    "current_price": info.get("currentPrice"),
                    "target_high_price": info.get("targetHighPrice"),
                    "target_low_price": info.get("targetLowPrice"),
                    "target_mean_price": info.get("targetMeanPrice"),
                    "target_median_price": info.get("targetMedianPrice"),
                    "number_of_analyst_opinions": info.get("numberOfAnalystOpinions")
                }
                result = {
                    "symbol": arguments["symbol"],
                    "price_targets": price_targets
                }

            elif tool_name == "get_ticker_institutional_holders":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "institutional_holders": self.df_to_dict(ticker.institutional_holders)
                }

            elif tool_name == "get_ticker_major_holders":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "major_holders": self.df_to_dict(ticker.major_holders)
                }

            elif tool_name == "get_ticker_insider_transactions":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "insider_transactions": self.df_to_dict(ticker.insider_transactions)
                }

            elif tool_name == "get_ticker_news":
                ticker = yf.Ticker(arguments["symbol"])
                max_items = arguments.get("max_items", 10)
                news = ticker.news[:max_items] if ticker.news else []
                result = {
                    "symbol": arguments["symbol"],
                    "count": len(news),
                    "news": news
                }

            elif tool_name == "get_ticker_options":
                ticker = yf.Ticker(arguments["symbol"])
                options = ticker.options
                result = {
                    "symbol": arguments["symbol"],
                    "expiration_dates": list(options) if options else []
                }

            elif tool_name == "get_ticker_option_chain":
                ticker = yf.Ticker(arguments["symbol"])
                option_chain = ticker.option_chain(arguments["expiration_date"])
                result = {
                    "symbol": arguments["symbol"],
                    "expiration_date": arguments["expiration_date"],
                    "calls": self.df_to_dict(option_chain.calls),
                    "puts": self.df_to_dict(option_chain.puts)
                }

            elif tool_name == "get_ticker_isin":
                ticker = yf.Ticker(arguments["symbol"])
                result = {
                    "symbol": arguments["symbol"],
                    "isin": ticker.isin
                }

            else:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Unknown tool: {tool_name}"
                    }],
                    "isError": True
                }

            # Return successful result
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }]
            }

        except Exception as e:
            logging.error(f"Error executing {tool_name}: {e}", exc_info=True)
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error: {str(e)}"
                }],
                "isError": True
            }

    def handle_request(self, request: dict) -> dict:
        """Route request to appropriate handler"""
        method = request.get("method", "")
        params = request.get("params", {})

        # Handle notifications (no response needed)
        if method.startswith("notifications/"):
            logging.debug(f"Received notification: {method}")
            return None

        if method == "initialize":
            return self.handle_initialize(params)
        elif method == "tools/list":
            return self.handle_tools_list(params)
        elif method == "tools/call":
            return self.handle_tools_call(params)
        else:
            raise ValueError(f"Unknown method: {method}")

    def run(self):
        """Main stdio loop"""
        logging.info("Yahoo Finance MCP Server starting...")

        for line in sys.stdin:
            try:
                line = line.strip()
                if not line:
                    continue

                logging.debug(f"Received: {line}")
                request = json.loads(line)

                result = self.handle_request(request)

                # Only send response for requests, not notifications
                if result is not None:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": result
                    }

                    response_json = json.dumps(response)
                    logging.debug(f"Sending: {response_json}")

                    sys.stdout.write(response_json + "\n")
                    sys.stdout.flush()

            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON: {e}")
            except Exception as e:
                logging.error(f"Error processing request: {e}", exc_info=True)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()

if __name__ == "__main__":
    server = MCPServer()
    server.run()
