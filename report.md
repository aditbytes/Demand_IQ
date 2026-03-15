# DemandIQ - Comprehensive Project Report

**Retail Demand Forecasting & Replenishment Engine**

> Predicts next-week sales for every product in every store and tells the manager how much to reorder to avoid stockouts and overstock.

---

## 📋 Executive Summary

DemandIQ is a **production-grade** retail demand forecasting and replenishment engine that:

1. **Predicts** next-week sales for every product in every store
2. **Recommends** optimal reorder quantities to prevent stockouts
3. **Classifies** inventory risk levels (LOW/MED/HIGH)
4. **Delivers** insights via FastAPI backend and Streamlit dashboard
5. **Notifies** store managers via Telegram bot integration

---

## 🏗️ System Architecture

```
Raw CSV (Walmart M5 Dataset)
         ↓
┌─────────────────────────────────┐
│     Data Ingestion Pipeline     │
│   (ingest.py → clean.py)        │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│     Feature Engineering         │
│   (feature_engineering.py)      │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│     ML Forecasting Models       │
│   (Prophet + XGBoost)           │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│   Reorder Decision Engine       │
│   (safety_stock + reorder)      │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│     FastAPI Backend             │
│     (REST API)                  │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│   Streamlit Web Dashboard       │
│   + Telegram Notifications      │
└─────────────────────────────────┘
```

---

## 📁 Complete Project Structure

```
DemandIQ/
├── 📂 api/
│   └── main.py                    # FastAPI application (264 lines)
│
├── 📂 dashboard/
│   └── app.py                     # Streamlit dashboard (875 lines)
│
├── 📂 data/
│   ├── 📂 raw/
│   │   ├── sales.csv              # Original sales data
│   │   ├── calendar.csv           # Calendar metadata
│   │   └── prices.csv             # Pricing data
│   ├── 📂 processed/
│   │   └── sales_cleaned.csv      # Cleaned sales data
│   ├── 📂 features/
│   │   └── features.csv           # Engineered ML features
│   └── reorders.csv               # Reorder recommendations
│
├── 📂 inventory/
│   ├── reorder.py                 # Reorder quantity calculations
│   ├── safety_stock.py            # Safety stock calculations
│   └── safety_stock_results.csv   # Safety stock results
│
├── 📂 logs/
│   └── telegram_notifications.log # Notification logs
│
├── 📂 mlruns/                     # MLflow experiment tracking
│
├── 📂 models/
│   ├── 📂 saved/
│   │   ├── 📂 prophet/            # Saved Prophet models (.pkl)
│   │   ├── 📂 xgboost/            # Saved XGBoost models (.pkl)
│   │   ├── prophet_results.csv    # Prophet training results
│   │   └── xgboost_results.csv    # XGBoost training results
│   ├── train_prophet.py           # Prophet model training
│   ├── train_xgboost.py           # XGBoost model training
│   └── evaluate.py                # Model evaluation
│
├── 📂 pipelines/
│   ├── ingest.py                  # Data ingestion
│   ├── clean.py                   # Data cleaning
│   └── feature_engineering.py     # Feature engineering
│
├── 📂 utils/
│   ├── __init__.py                # Package initializer
│   └── telegram_notifier.py       # Telegram notifications
│
├── mlflow.db                      # MLflow SQLite database
├── requirements.txt               # Python dependencies
├── run_pipeline.sh                # Pipeline runner script
├── README.md                      # Project documentation
├── SETUP.md                       # Setup guide
├── REAL_DATA_SETUP.md             # Real data configuration
├── REAL_WORLD_IMPACT.md           # Business impact documentation
└── WEBPAGE_PROMPT.md              # Marketing website prompt
```

---

## 🛠️ Technology Stack

| Layer              | Technology     | Version   |
|--------------------|----------------|-----------|
| **Data**           | Pandas         | ≥2.0.0    |
|                    | NumPy          | ≥1.24.0   |
| **Storage**        | CSV Files      | N/A       |
| **ML Models**      | Prophet        | ≥1.1.0    |
|                    | XGBoost        | ≥2.0.0    |
|                    | Scikit-learn   | ≥1.3.0    |
| **API**            | FastAPI        | ≥0.104.0  |
|                    | Uvicorn        | ≥0.24.0   |
|                    | Pydantic       | ≥2.0.0    |
| **Dashboard**      | Streamlit      | ≥1.28.0   |
|                    | Plotly         | ≥5.17.0   |
| **Experiment Tracking** | MLflow    | ≥2.8.0    |
| **Notifications**  | Telegram API   | HTTP      |
| **Utilities**      | python-dotenv  | ≥1.0.0    |
|                    | requests       | ≥2.31.0   |
|                    | scipy          | ≥1.11.0   |

---

## 🔧 Feature Details

### 1. Data Pipelines

#### `pipelines/ingest.py`
- Loads raw M5 dataset (Walmart sales data)
- Validates data integrity
- Initial preprocessing

#### `pipelines/clean.py`
- Removes missing values
- Handles outliers
- Saves cleaned data to `data/processed/sales_cleaned.csv`

#### `pipelines/feature_engineering.py`
Creates ML-ready features including:

| Feature Type | Features |
|--------------|----------|
| **Lag Features** | `lag7`, `lag14`, `lag28` |
| **Rolling Statistics** | `rolling7_mean`, `rolling7_std`, `rolling30_mean`, `rolling30_std` |
| **Price Features** | `price`, `price_change` |
| **Calendar Features** | `day_of_week`, `month`, `day_of_month`, `week_of_year` |
| **Event Features** | `is_holiday`, `is_snap`, `promo` |

---

### 2. Machine Learning Models

#### Prophet Model (`models/train_prophet.py`)
- **Algorithm**: Facebook Prophet time-series forecasting
- **Features**:
  - Weekly and yearly seasonality
  - US holiday effects
  - Automatic changepoint detection
- **Output**: 7-day demand forecast

#### XGBoost Model (`models/train_xgboost.py`)
- **Algorithm**: Gradient Boosting with XGBoost
- **Hyperparameters**:
  ```python
  {
      'objective': 'reg:squarederror',
      'max_depth': 6,
      'learning_rate': 0.1,
      'n_estimators': 100,
      'subsample': 0.8,
      'colsample_bytree': 0.8
  }
  ```
- **Features Used**: All engineered features (lags, rolling stats, price, calendar)
- **Train/Test Split**: 80/20 chronological

#### Model Evaluation (`models/evaluate.py`)
- Compares model performance using MAE (Mean Absolute Error)
- Selects best model per SKU automatically
- Results tracked via MLflow

---

### 3. Inventory Management

#### Safety Stock Calculation (`inventory/safety_stock.py`)
```
Safety Stock = Z × σ × √(lead_time)
```
Where:
- **Z** = 1.65 (95% service level)
- **σ** = Standard deviation of demand
- **lead_time** = Days from order to delivery (default: 7 days)

#### Reorder Engine (`inventory/reorder.py`)
```
Reorder Qty = Forecast + Safety Stock - Current Stock
```

#### Risk Classification
| Risk Level | Condition | Badge |
|------------|-----------|-------|
| **HIGH** | Current stock < 3 days of forecasted demand | 🔴 |
| **MED** | Current stock < 7 days of forecasted demand | 🟡 |
| **LOW** | Adequate stock levels | 🟢 |

---

### 4. FastAPI Backend (`api/main.py`)

#### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API root with endpoint list |
| `GET` | `/forecast/{store_id}/{sku}` | Get demand forecast |
| `GET` | `/reorder/{store_id}/{sku}` | Get reorder recommendation |
| `GET` | `/alerts` | Get at-risk products |
| `GET` | `/health` | Health check |

#### Example Responses

**Forecast Response:**
```json
{
  "store_id": "CA_1",
  "sku": "HOBBIES_1_001",
  "forecast_period_days": 7,
  "forecasts": [
    {"date": "2024-01-01", "predicted_demand": 12.5}
  ]
}
```

**Reorder Response:**
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

---

### 5. Streamlit Dashboard (`dashboard/app.py`)

#### Features
- **Store Manager View**: Select store and product for detailed analysis
- **Sales History Chart**: Last 180 days with interactive Plotly visualization
- **Forecast Curve**: 14-day demand forecast overlay
- **Reorder Cards**: Current stock, forecast, safety stock, recommended order quantity
- **At-Risk Products Table**: Sortable by risk level, stock, forecast
- **Category Breakdown**: Pie chart visualization
- **Multi-Store Support**: 10 stores with varied inventory

#### Store Configuration
| Store ID | Name | Region | Type |
|----------|------|--------|------|
| STORE-001 | Downtown Central | Northeast | Supermarket |
| STORE-002 | Mall Express | Southeast | Express |
| STORE-003 | Suburban Fresh | Midwest | Supermarket |
| STORE-004 | Highway Outlet | Southwest | Convenience |
| STORE-005 | Metro Market | West | Supermarket |
| STORE-006 | Village Store | Northeast | Convenience |
| STORE-007 | Airport Shop | Southeast | Express |
| STORE-008 | University Campus | Midwest | Express |
| STORE-009 | Beachside Market | West | Supermarket |
| STORE-010 | City Center | Central | Hypermarket |

#### Product Catalog (Sample)
- **Dairy**: Fresh Whole Milk, Organic Skim Milk
- **Bakery**: White Bread Loaf, Whole Wheat Bread
- **Eggs**: Free-Range Eggs, Organic Eggs
- **Breakfast**: Butter, Cheese, Yogurt
- **Beverages**: Orange Juice, Apple Juice, Ground Coffee, Green Tea
- **Cereals**: Corn Flakes, Muesli, Rolled Oats
- **Snacks**: Potato Chips, Ice Cream
- **Frozen**: Frozen Pizza

---

### 6. Telegram Notifications (`utils/telegram_notifier.py`)

#### Features
- Real-time reorder alerts
- Risk-level color coding
- Timestamp logging
- Connection testing utility

#### Message Format
```
📦 REORDER PLACED

🏪 Store: STORE-001
🏷️ SKU: SKU-MILK-001
📊 Order Quantity: 150 units

🔴 Risk Level: HIGH

Inventory Details:
• Current Stock: 50 units
• Forecasted Demand: 181 units
• Safety Stock: 36 units

⏰ Timestamp: 2026-02-03 17:55:33

— DemandIQ System
```

---

## 📊 Data Files

| File | Location | Description |
|------|----------|-------------|
| `sales.csv` | `data/raw/` | Original Walmart M5 sales data |
| `calendar.csv` | `data/raw/` | Calendar with events/holidays |
| `prices.csv` | `data/raw/` | Product pricing data |
| `sales_cleaned.csv` | `data/processed/` | Cleaned sales transactions |
| `features.csv` | `data/features/` | Engineered ML features |
| `forecast.csv` | `data/` | Model predictions |
| `reorders.csv` | `data/` | Reorder recommendations |
| `safety_stock_results.csv` | `inventory/` | Safety stock calculations |

---

## 🚀 Quick Start Commands

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run data pipelines
python pipelines/ingest.py
python pipelines/clean.py
python pipelines/feature_engineering.py

# 4. Train ML models
python models/train_prophet.py --subset 10
python models/train_xgboost.py --subset 10

# 5. Generate reorder recommendations
python inventory/safety_stock.py
python inventory/reorder.py

# 6. Start API server
uvicorn api.main:app --reload

# 7. Launch dashboard
streamlit run dashboard/app.py

# 8. View MLflow experiments
mlflow ui
```

---

## 📈 Future Enhancements

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

## 📝 Documentation Files

| File | Description |
|------|-------------|
| `README.md` | Main project documentation |
| `SETUP.md` | Installation and setup guide |
| `REAL_DATA_SETUP.md` | Real data configuration guide |
| `REAL_WORLD_IMPACT.md` | Business impact analysis |
| `WEBPAGE_PROMPT.md` | Marketing website prompt |

---

## 📄 License

MIT License

---

**Report Generated**: February 3, 2026  
**DemandIQ** - *Turning ML into Money* 💰
