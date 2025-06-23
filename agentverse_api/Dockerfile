FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY agentverse_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and dependencies
COPY agentverse_api ./agentverse_api/
COPY src ./src/
COPY config ./config/
# Copy additional dependencies from parent directory
COPY mcp_agent_client.py ./
COPY servicenow_agent_adapter.py ./
COPY servicenow_config_loader.py ./

# Set Python path
ENV PYTHONPATH=/app

# Create pipelines directory
RUN mkdir -p /app/pipelines

# Create non-root user
RUN useradd -m -u 1000 agentverse && chown -R agentverse:agentverse /app
USER agentverse

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "agentverse_api.main:app", "--host", "0.0.0.0", "--port", "8000"]