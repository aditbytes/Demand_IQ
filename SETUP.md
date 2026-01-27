# DemandIQ - Setup Guide

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] PostgreSQL 12 or higher installed and running
- [ ] At least 4GB RAM available
- [ ] 2GB free disk space for data
- [ ] Git installed (optional, for version control)

## Step-by-Step Setup

### 1. Create PostgreSQL Database

```bash
# Create database
createdb demandiq

# Verify connection
psql -d demandiq -c "SELECT version();"
```

### 2. Set Up Python Environment

```bash
# Navigate to project directory
cd /Users/aditya/CODING/demand_IQ

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Verify activation (should show venv path)
which python
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify key packages
python -c "import pandas, fastapi, streamlit, prophet, xgboost; print('✓ All packages installed')"
```

### 4. Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit .env file with your database credentials
# Change DB_PASSWORD to your PostgreSQL password
nano .env
```

Example `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=demandiq
DB_USER=postgres
DB_PASSWORD=your_actual_password
```

### 5. Initialize Database Schema

```bash
# Run schema file
psql -d demandiq -f db/schema.sql

# Verify tables created
psql -d demandiq -c "\dt"
```

You should see 5 tables: `sales`, `features`, `forecast`, `inventory`, `reorders`

### 6. Test Database Connection

```bash
python -c "from db.db_utils import test_connection; test_connection()"
```

Expected output: `✓ Successfully connected to database: demandiq`

## Running the Full Pipeline

### Option A: Automated (Recommended)

```bash
# Make script executable
chmod +x run_pipeline.sh

# Run entire pipeline
./run_pipeline.sh
```

This will:
1. Download M5 dataset
2. Clean and process data
3. Engineer features
4. Generate sample inventory
5. Train Prophet and XGBoost models
6. Calculate safety stocks
7. Generate reorder recommendations

**Expected time**: 15-30 minutes (depending on subset size)

### Option B: Manual (Step by Step)

```bash
# Step 1: Data ingestion
python pipelines/ingest.py

# Step 2: Data cleaning
python pipelines/clean.py

# Step 3: Feature engineering
python pipelines/feature_engineering.py

# Step 4: Generate sample inventory
python db/generate_sample_data.py

# Step 5: Train models
python models/train_prophet.py --subset 20
python models/train_xgboost.py --subset 20
python models/evaluate.py

# Step 6: Generate recommendations
python inventory/safety_stock.py
python inventory/reorder.py
```

## Launching the System

### 1. Start MLflow (Optional - for viewing experiments)

```bash
# In a new terminal
mlflow ui

# Open in browser: http://localhost:5000
```

### 2. Start FastAPI Backend

```bash
# In a new terminal
uvicorn api.main:app --reload

# API available at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### 3. Start Streamlit Dashboard

```bash
# In a new terminal
streamlit run dashboard/app.py

# Dashboard opens automatically in browser
# Or navigate to: http://localhost:8501
```

## Testing the System

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get forecast (replace with actual store_id and sku from your data)
curl http://localhost:8000/forecast/CA_1/HOBBIES_1_001

# Get reorder recommendation
curl http://localhost:8000/reorder/CA_1/HOBBIES_1_001

# Get alerts
curl http://localhost:8000/alerts?risk_level=HIGH
```

### Test Dashboard

1. Open dashboard at http://localhost:8501
2. Select a store from dropdown
3. Select a SKU
4. Verify:
   - Sales history chart loads
   - Forecast is displayed
   - Reorder recommendation shows
   - At-risk products table appears

## Troubleshooting

### Issue: Database connection failed

**Solution:**
- Verify PostgreSQL is running: `pg_isready`
- Check credentials in `.env` file
- Ensure database exists: `psql -l | grep demandiq`

### Issue: ModuleNotFoundError

**Solution:**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall requirements: `pip install -r requirements.txt`

### Issue: Prophet installation fails

**Solution (macOS):**
```bash
# Install command line tools
xcode-select --install

# Install via conda instead
conda install -c conda-forge prophet
```

### Issue: No data in dashboard

**Solution:**
- Verify pipelines ran successfully
- Check database: `psql -d demandiq -c "SELECT COUNT(*) FROM sales;"`
- Re-run pipelines if needed

### Issue: MLflow tracking not working

**Solution:**
- Create mlruns directory: `mkdir -p mlruns`
- Check file permissions
- Set environment variable: `export MLFLOW_TRACKING_URI=file:./mlruns`

## Next Steps

Once everything is running:

1. ✅ Explore the dashboard interface
2. ✅ Test API endpoints with different store-SKU combinations
3. ✅ Review MLflow experiments to compare model performance
4. ✅ Examine reorder recommendations for different risk levels
5. ✅ Consider training on full dataset (remove `--subset` flag)

## Production Deployment Considerations

For production deployment:

- [ ] Use Docker containers
- [ ] Set up Airflow for daily pipeline runs
- [ ] Deploy PostgreSQL to managed service (RDS, Cloud SQL)
- [ ] Deploy API to cloud (AWS ECS, GCP Cloud Run)
- [ ] Add authentication to API endpoints
- [ ] Set up monitoring and alerts
- [ ] Implement data validation checks
- [ ] Add comprehensive error logging
- [ ] Create automated backup system

---

**Need help?** Review the main [README.md](README.md) for detailed documentation.
