# DemandIQ

**Retail Demand Forecasting & Replenishment Engine**

> Predicts next-week sales for every product in every store and tells the manager how much to reorder to avoid stockouts and overstock.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What This System Does

DemandIQ is a **production-grade** retail demand forecasting and replenishment engine that:

1. **Predicts** next-week sales for every product in every store
2. **Recommends** optimal reorder quantities to prevent stockouts
3. **Classifies** inventory risk levels (LOW/MED/HIGH)
4. **Delivers** insights via FastAPI backend and Streamlit dashboard

This is not a notebook. This is a **production system** built with FAANG-level engineering standards.

---

## 🏗️ Architecture

```
Raw CSV (Walmart M5)
        ↓
Data Ingestion (Python)
        ↓
CSV Feature Store
        ↓
ML Forecasting Models
        ↓
Reorder Decision Engine
        ↓
FastAPI
        ↓
Web Dashboard
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Data** | Pandas, NumPy |
| **Storage** | CSV files |
| **ML Models** | Prophet, XGBoost |
| **API** | FastAPI |
| **Dashboard** | Streamlit |
| **Visualization** | Plotly |
| **Tracking** | MLflow |
| **Version Control** | Git |

---

## 📁 Project Structure

```
DemandIQ/
├── data/
│   ├── raw/              # Original M5 datasets
│   ├── processed/        # Cleaned data (CSV)
│   └── features/         # Engineered features
├── pipelines/
│   ├── ingest.py         # Data ingestion
│   ├── clean.py          # Data cleaning
│   └── feature_engineering.py
├── models/
│   ├── train_prophet.py  # Prophet model
│   ├── train_xgboost.py  # XGBoost model
│   └── evaluate.py       # Model evaluation
├── inventory/
│   ├── safety_stock.py   # Safety stock calculations
│   └── reorder.py        # Reorder logic
├── api/
│   └── main.py           # FastAPI application
├── dashboard/
│   └── app.py            # Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9+
- 4GB+ RAM

### 2. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd demand_IQ

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Data Pipelines

```bash
# Step 1: Ingest raw data
python pipelines/ingest.py

# Step 2: Clean and save to CSV
python pipelines/clean.py

# Step 3: Engineer features
python pipelines/feature_engineering.py
```

### 4. Train Models

```bash
# Train Prophet models (on subset for speed)
python models/train_prophet.py --subset 10

# Train XGBoost models
python models/train_xgboost.py --subset 10

# Evaluate and select best models
python models/evaluate.py

# View MLflow experiments
mlflow ui
# Open: http://localhost:5000
```

### 5. Generate Inventory Recommendations

```bash
# Calculate safety stocks
python inventory/safety_stock.py

# Generate reorder recommendations
python inventory/reorder.py
```

### 6. Launch API

```bash
# Start FastAPI server
uvicorn api.main:app --reload

# API will be available at: http://localhost:8000
# Auto-generated docs: http://localhost:8000/docs
```

### 7. Launch Dashboard

```bash
# Start Streamlit dashboard
streamlit run dashboard/app.py

# Dashboard will open in browser automatically
```

---

## 📊 Data Storage

### CSV Files

All data is stored in CSV format in the `data/` directory:

**sales_cleaned.csv** - Historical sales transactions
- `date`, `store_id`, `sku`, `units`, `price`, `promo`

**features.csv** - Engineered ML features
- Lag features: `lag7`, `lag14`, `lag28`
- Rolling stats: `rolling7_mean`, `rolling30_mean`
- Calendar: `day_of_week`, `month`, `is_holiday`

**forecast.csv** - Model predictions
- `forecast_date`, `store_id`, `sku`, `predicted_demand`

**reorders.csv** - Reorder recommendations
- `store_id`, `sku`, `order_qty`, `risk_level`

---

## 🤖 ML Models

### 1. Baseline
- **Algorithm**: Naive (last week = this week)
- **Use Case**: Benchmark comparison

### 2. Prophet
- **Algorithm**: Facebook Prophet
- **Features**: Automatic seasonality, US holidays
- **Best For**: Products with strong seasonal patterns

### 3. XGBoost
- **Algorithm**: Gradient boosting
- **Features**: Lags (7,14,28), rolling means, price, promos
- **Best For**: Complex demand patterns

**Model Selection**: Best model per SKU based on lowest MAE.

---

## 🔧 Reorder Engine

### Safety Stock Formula

```
Safety Stock = Z × σ × √(lead_time)
```

Where:
- **Z** = 1.65 (95% service level)
- **σ** = Standard deviation of demand
- **lead_time** = Days from order to delivery

### Reorder Quantity

```
Reorder Qty = Forecast + Safety Stock - Current Stock
```

### Risk Classification

- **🔴 HIGH**: Current stock < 3 days of forecasted demand
- **🟡 MED**: Current stock < 7 days of forecasted demand
- **🟢 LOW**: Adequate stock levels

---

## 🌐 API Endpoints

### Base URL: `http://localhost:8000`

#### 1. Get Forecast
```http
GET /forecast/{store_id}/{sku}
```

**Response:**
```json
{
  "store_id": "CA_1",
  "sku": "HOBBIES_1_001",
  "forecast_period_days": 7,
  "forecasts": [
    {"date": "2024-01-01", "predicted_demand": 12.5},
    ...
  ]
}
```

#### 2. Get Reorder Recommendation
```http
GET /reorder/{store_id}/{sku}
```

**Response:**
```json
{
  "store_id": "CA_1",
  "sku": "HOBBIES_1_001",
  "current_stock": 50,
  "forecasted_demand": 85.3,
  "safety_stock": 15.2,
  "reorder_qty": 50,
  "risk_level": "MED"
}
```

#### 3. Get Alerts
```http
GET /alerts?risk_level=HIGH&limit=50
```

**Response:**
```json
[
  {
    "store_id": "CA_1",
    "sku": "FOODS_3_090",
    "current_stock": 10,
    "forecasted_demand": 45.0,
    "reorder_qty": 55,
    "risk_level": "HIGH"
  },
  ...
]
```

---

## 📈 Dashboard Features

### Store Manager View

1. **Sales History Chart**
   - Last 90 days of actual sales
   - Interactive Plotly visualization

2. **Forecast Curve**
   - 7-day demand forecast
   - Overlaid on historical data

3. **Reorder Recommendation Card**
   - Current stock level
   - Forecasted demand
   - Safety stock buffer
   - **Recommended order quantity** (prominent)
   - Risk badge (color-coded)

4. **At-Risk Products Table**
   - All HIGH/MED risk items
   - Sortable by risk, stock, forecast
   - Quick-order buttons

---

## 🧪 Testing & Validation

### Data Pipeline Test
```bash
python pipelines/ingest.py
python pipelines/clean.py
python pipelines/feature_engineering.py

# Verify CSV files created
ls -la data/processed/
```

### Model Test
```bash
# Quick test on 10 SKUs
python models/train_prophet.py --subset 10
python models/train_xgboost.py --subset 10

# Check MLflow UI
mlflow ui
```

### API Test
```bash
# Start API
uvicorn api.main:app --reload

# Test endpoints
curl http://localhost:8000/forecast/CA_1/HOBBIES_1_001
curl http://localhost:8000/reorder/CA_1/HOBBIES_1_001
curl http://localhost:8000/alerts?risk_level=HIGH

# View auto-docs
open http://localhost:8000/docs
```

### Dashboard Test
```bash
streamlit run dashboard/app.py
```

---

## 🎓 Why This Stack?

This project uses **industry-standard** technologies that FAANG companies use in production:

- **FastAPI**: Modern, fast API framework (used by Uber, Netflix)
- **Prophet**: Battle-tested forecasting (developed by Facebook)
- **XGBoost**: SOTA gradient boosting (Kaggle competition winner)
- **Streamlit**: Rapid dashboard development (used by Snowflake)
- **MLflow**: Experiment tracking (used by Databricks, Microsoft)

---

## 📝 Future Enhancements

- [ ] Docker containerization
- [ ] Airflow orchestration for daily pipeline runs
- [ ] Multi-store inventory optimization
- [ ] A/B testing framework for model comparisons
- [ ] Real-time data streaming (Kafka)
- [ ] Cloud deployment (AWS/GCP/Azure)
- [ ] Mobile app for store managers
- [ ] Advanced models (LSTM, Transformers)
- [ ] Multi-objective optimization (cost vs. service level)
- [ ] Database integration (PostgreSQL/MySQL) for production scale

---

## 👥 Contributors

---

### 🗄️ Alok — Data Engineering
Designed and implemented the retail data ingestion and preprocessing pipeline using Walmart M5-style synthetic data generation. Built raw data transformation (wide-to-long conversion), calendar and pricing data integration, cleaning workflows, and processed dataset export for downstream analytics.

---

### 🤖 Aditya — Model Training
Designed dual-model forecasting framework using Prophet and XGBoost.
Conducted hyperparameter tuning and MLflow experiment tracking.

---

### 📊 Abhimanyu — Dashboard Development
Built Streamlit dashboard with Plotly visualizations for sales history,
forecasts, and inventory risk classification.

---

### 🌐 Ankita — API Development
Developed FastAPI backend with RESTful endpoints, CORS middleware, and Pydantic validation.

---

### ⚙️ Surbhit — Feature Engineering & Pipeline Orchestration
Developed temporal feature engineering modules including lag features, rolling statistics, price-based transformations, and calendar-driven feature extraction to create ML-ready datasets for forecasting models.

---

## 👨‍💻 Author

Built with FAANG-level engineering standards

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- **Walmart M5 Dataset**: Kaggle M5 Forecasting - Accuracy competition
- **Prophet**: Facebook Research
- **XGBoost**: DMLC

---

**DemandIQ** - *Turning ML into Money* 💰
