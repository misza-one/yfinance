FROM python:3.11-slim

WORKDIR /app

# Copy requirements files
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy yfinance package
COPY yfinance/ ./yfinance/
COPY setup.py ./
COPY README.md ./
COPY LICENSE.txt ./
COPY MANIFEST.in ./

# Install yfinance package
RUN pip install -e .

# Copy MCP stdio server
COPY mcp_stdio_server.py ./

# Make executable
RUN chmod +x mcp_stdio_server.py

# Run the MCP stdio server
CMD ["python", "-u", "/app/mcp_stdio_server.py"]
