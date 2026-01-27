#!/bin/bash
# DemandIQ - Full Pipeline Runner
# Runs all data pipelines, model training, and recommendation generation

echo "======================================"
echo "DemandIQ - Full Pipeline Execution"
echo "======================================"
echo ""

# Step 1: Data Ingestion
echo "Step 1/7: Data Ingestion..."
python pipelines/ingest.py
if [ $? -ne 0 ]; then
    echo "✗ Data ingestion failed"
    exit 1
fi
echo ""

# Step 2: Data Cleaning
echo "Step 2/7: Data Cleaning..."
python pipelines/clean.py
if [ $? -ne 0 ]; then
    echo "✗ Data cleaning failed"
    exit 1
fi
echo ""

# Step 3: Feature Engineering
echo "Step 3/7: Feature Engineering..."
python pipelines/feature_engineering.py
if [ $? -ne 0 ]; then
    echo "✗ Feature engineering failed"
    exit 1
fi
echo ""

# Step 4: Generate Sample Inventory
echo "Step 4/7: Generating Sample Inventory..."
python db/generate_sample_data.py
if [ $? -ne 0 ]; then
    echo "✗ Sample data generation failed"
    exit 1
fi
echo ""

# Step 5: Model Training (subset for speed)
echo "Step 5/7: Training Models..."
echo "  Training Prophet..."
python models/train_prophet.py --subset 20
echo "  Training XGBoost..."
python models/train_xgboost.py --subset 20
echo "  Evaluating models..."
python models/evaluate.py
echo ""

# Step 6: Safety Stock Calculation
echo "Step 6/7: Calculating Safety Stock..."
python inventory/safety_stock.py
if [ $? -ne 0 ]; then
    echo "✗ Safety stock calculation failed"
    exit 1
fi
echo ""

# Step 7: Reorder Recommendations
echo "Step 7/7: Generating Reorder Recommendations..."
python inventory/reorder.py
if [ $? -ne 0 ]; then
    echo "✗ Reorder generation failed"
    exit 1
fi
echo ""

echo "======================================"
echo "✓ Pipeline execution complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Launch API: uvicorn api.main:app --reload"
echo "  2. Launch Dashboard: streamlit run dashboard/app.py"
echo "  3. View MLflow: mlflow ui"
