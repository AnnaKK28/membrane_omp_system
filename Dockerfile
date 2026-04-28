# Multi-stage Dockerfile for Railway deployment
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# Copy data directory with pre-built database
COPY data/ ./data/

# Copy model and data
COPY XGBoost_mem_OMPS_model.json /workspace/XGBoost_mem_OMPS_model.json
COPY data_set.xlsx /workspace/data_set.xlsx

# Set environment
ENV PYTHONPATH=/app/backend
ENV PORT=5000

# Ensure data directory is writable
RUN chmod 755 /app/data

EXPOSE 5000

CMD ["python", "-m", "backend.app"]