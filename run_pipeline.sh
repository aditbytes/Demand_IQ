#!/bin/bash
# DemandIQ - Full Pipeline Runner
# Runs all data pipelines, model training, and recommendation generation

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "======================================"
echo "DemandIQ - Full Pipeline Execution"
echo "======================================"
echo ""

# Step 1: Data Generation
echo "Step 1/6: Generating Sample Data..."
python3 pipelines/ingest.py
if [ $? -ne 0 ]; then
    echo "✗ Data generation failed"
    exit 1
fi
echo ""

# Step 2: Data Cleaning
echo "Step 2/6: Data Cleaning..."
python3 pipelines/clean.py
if [ $? -ne 0 ]; then
    echo "✗ Data cleaning failed"
    exit 1
fi
echo ""

# Step 3: Feature Engineering
echo "Step 3/6: Feature Engineering..."
python3 pipelines/feature_engineering.py
if [ $? -ne 0 ]; then
    echo "✗ Feature engineering failed"
    exit 1
fi
echo ""

# Step 4: Model Training (optional - skip if dependencies missing)
echo "Step 4/6: Training Models..."
echo "  Note: Model training requires prophet and mlflow packages"
echo "  Skipping model training for quick demo..."
echo "  (Run manually: python3 models/train_prophet.py --subset 10)"
echo ""

# Step 5: Safety Stock Calculation
echo "Step 5/6: Calculating Safety Stock..."
python3 inventory/safety_stock.py
if [ $? -ne 0 ]; then
    echo "✗ Safety stock calculation failed"
    exit 1
fi
echo ""

# Step 6: Reorder Recommendations
echo "Step 6/6: Generating Reorder Recommendations..."
python3 inventory/reorder.py
if [ $? -ne 0 ]; then
    echo "✗ Reorder generation failed"
    exit 1
fi
echo ""

echo "======================================"
echo "✓ Pipeline execution complete!"
echo "======================================"
echo ""
echo "Data files created:"
echo "  - data/raw/ (sample sales, calendar, prices)"
echo "  - data/processed/sales_cleaned.csv"
echo "  - data/features/features.csv"
echo "  - data/reorders.csv"
echo ""
echo "Next steps:"
echo "  1. Launch Dashboard: streamlit run dashboard/app.py"
echo "  2. Launch API: uvicorn api.main:app --reload"
