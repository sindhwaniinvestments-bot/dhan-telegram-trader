# Dockerfile for 24/7 Cloud Deployment of Telegram Trade Tracker Agent
FROM python:3.10-slim

WORKDIR /app

# Copy requirements & install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Run the 24/7 background trade tracker daemon
CMD ["python", "run_daemon.py"]
