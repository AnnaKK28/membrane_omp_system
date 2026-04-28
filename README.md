# Membrane OMP System
# 膜分离性能预测与有机污染物截留数据库系统

A full-stack web application for predicting membrane separation performance and organic micropollutant (OMP) rejection rates using XGBoost machine learning.

## 🏗️ Architecture

```
membrane_omp_system/
├── backend/                 # Flask API backend
│   ├── app.py              # Main Flask application
│   ├── database.py         # SQLite database models
│   ├── import_data.py      # Excel data import script
│   ├── routes/             # API route blueprints
│   │   ├── solute.py       # Solute/pollutant APIs
│   │   ├── membrane.py     # Membrane APIs
│   │   └── predict.py      # ML prediction API
│   └── ml_model/           # ML model loader
│       └── predictor.py    # XGBoost predictor
├── frontend/               # Vue 3 SPA
│   ├── src/
│   │   ├── views/          # Page components
│   │   ├── api/            # API client
│   │   └── router/         # Vue Router
│   └── package.json
├── docker/                 # Docker configurations
└── requirements.txt
```

## 🔧 Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | Vue 3 + Element Plus + ECharts     |
| Backend    | Python Flask                       |
| Database   | SQLite (dev)                       |
| ML         | XGBoost Regressor                  |
| Deployment | Docker + Nginx                     |

## 🚀 Quick Start

### Backend (Local Development)

```bash
cd membrane_omp_system
pip install -r requirements.txt

# Initialize database and import data
cd backend
python import_data.py

# Start Flask API
python app.py
```

Backend runs at: http://localhost:5000

### Frontend (Local Development)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

### Docker Deployment

```bash
cd docker
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## 📡 API Endpoints

### Solute (Pollutant) APIs
| Method | Endpoint              | Description           |
|--------|-----------------------|-----------------------|
| GET    | `/api/solute/search`  | Search solutes by name (fuzzy) |
| GET    | `/api/solute/list`    | List solutes with pagination |
| GET    | `/api/solute/<id>`    | Get solute by ID |

### Membrane APIs
| Method | Endpoint                | Description            |
|--------|-------------------------|------------------------|
| GET    | `/api/membrane/search`  | Search membranes by name |
| GET    | `/api/membrane/list`    | List membranes with pagination |
| GET    | `/api/membrane/<id>`   | Get membrane by ID |

### Prediction APIs
| Method | Endpoint                        | Description                |
|--------|----------------------------------|----------------------------|
| POST   | `/api/predict`                  | Predict rejection rate     |
| GET    | `/api/experiments`              | List experiments (paginated) |
| GET    | `/api/statistics`               | Get dataset statistics     |
| GET    | `/api/chart/membrane_comparison` | Chart: membranes for solute |
| GET    | `/api/chart/solute_comparison`   | Chart: solutes for membrane |

## 🤖 ML Model

### Input Features
Feature vector order: `[MWCO, Contact angle, Zeta potential, MW, Neutral charge, Neutral logD]`

| Feature         | Source   | Description              |
|-----------------|----------|--------------------------|
| MW              | Solute   | Molecular weight         |
| charge          | Solute   | Neutral charge           |
| logD            | Solute   | Neutral logD             |
| MWCO            | Membrane | Molecular weight cutoff  |
| contact_angle   | Membrane | Contact angle            |
| zeta_potential  | Membrane | Zeta potential           |

### Prediction Example

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"solute_id": 1, "membrane_id": 1}'
```

Response:
```json
{
  "success": true,
  "data": {
    "solute_name": "Trimethoprim",
    "membrane_name": "(PIP+BA50)+TMC//PSf",
    "rejection_rate": 83.8,
    "features": {
      "MW": 290.323,
      "charge": 0.85,
      "logD": 1.10,
      "MWCO": 380,
      "contact_angle": 53.2,
      "zeta_potential": -72.7
    }
  }
}
```

## 📊 Features

1. **Pollutant Query System** - Fuzzy search with dropdown selection
2. **Membrane Query System** - Search and browse membrane parameters
3. **Rejection Rate Prediction** - ML-powered prediction via XGBoost
4. **Visualization Module** - ECharts bar/line charts for comparison
5. **Data Browser** - Paginated view of all experiments, solutes, membranes

## 📁 Data

- Model file: `XGBoost_mem_OMPS_model.json`
- Dataset: `data_set.xlsx` (793 experiment records)

## 🐳 Docker

Build and run with docker-compose:
```bash
cd docker
docker-compose up --build
```

This will start:
- Flask backend on port 5000
- Vue frontend on port 3000 (with Nginx)

## License

MIT