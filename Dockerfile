FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables from secrets
ENV DB_HOST=localhost \
    DB_PORT=5432 \
    DB_USER=postgres \
    DB_NAME=gourmet_guide \
    API_V1_PREFIX=/v1 \
    OPENROUTER_BASE_URL=https://openrouter.ai/api/v1 \
    OPENROUTER_MODEL=deepseek/deepseek-chat-v3-0324:free \
    ACCESS_TOKEN_EXPIRE_MINUTES=30 \
    LOG_FORMAT=json

# Command to run the application
CMD ["python", "run.py"]
