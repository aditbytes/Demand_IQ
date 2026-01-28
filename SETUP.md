# DemandIQ - Setup Guide

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] At least 4GB RAM available
- [ ] 2GB free disk space for data
- [ ] Git installed (optional, for version control)

## Step-by-Step Setup

### 1. Set Up Python Environment

```bash
# Navigate to project directory
cd /Volumes/Aditya\ ssd/Demand_IQ

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Verify activation (should show venv path)
which python
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify key packages
python -c "import pandas, fastapi, streamlit, prophet, xgboost; print('✓ All packages installed')"
```

### 3. Configure Environment Variables (Optional)

```bash
# Copy template (if using API keys or external services)
cp .env.example .env

# Edit .env file as needed
nano .env
```

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
2. Clean and process data (saved to CSV)
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

# Step 2: Data cleaning (saves to data/processed/)
python pipelines/clean.py

# Step 3: Feature engineering
python pipelines/feature_engineering.py

# Step 4: Train models
python models/train_prophet.py --subset 20
python models/train_xgboost.py --subset 20
python models/evaluate.py

# Step 5: Generate recommendations
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
- Check CSV files exist in `data/processed/` folder
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
- [ ] Deploy API to cloud (AWS ECS, GCP Cloud Run)
- [ ] Add authentication to API endpoints
- [ ] Set up monitoring and alerts
- [ ] Implement data validation checks
- [ ] Add comprehensive error logging
- [ ] Create automated backup system

---

**Need help?** Review the main [README.md](README.md) for detailed documentation.
