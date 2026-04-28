# Multi-stage build for Railway deployment
FROM python:3.11-slim as backend

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# Copy model and data
COPY XGBoost_mem_OMPS_model.json /workspace/XGBoost_mem_OMPS_model.json
COPY data_set.xlsx /workspace/data_set.xlsx

ENV PYTHONPATH=/app/backend
ENV PORT=5000
ENV DATA_DIR=/app/data

EXPOSE 5000

# Run backend
CMD ["python", "-m", "backend.app"]

---
# Frontend build stage (used locally, not on Railway)
FROM node:18-alpine as frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=frontend-builder /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]