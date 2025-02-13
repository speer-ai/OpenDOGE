FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Set up cron job
COPY scripts/cron/collect_daily.sh /etc/cron.daily/collect_data
RUN chmod +x /etc/cron.daily/collect_data

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy .env file if it exists, otherwise use .env.example
COPY .env* .
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Install app in development mode
RUN pip install -e .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN mkdir -p /var/log/opendoge && chown appuser:appuser /var/log/opendoge
RUN chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 