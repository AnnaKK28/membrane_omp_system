# Build stage for frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app

# Copy and install frontend dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Final stage - Python backend
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-builder /app/dist ./frontend/dist/

# Copy model and data
COPY XGBoost_mem_OMPS_model.json /workspace/XGBoost_mem_OMPS_model.json
COPY data_set.xlsx /workspace/data_set.xlsx

# Set environment
ENV PYTHONPATH=/app/backend
ENV PORT=5000

EXPOSE 5000

CMD ["python", "-m", "backend.app"]
