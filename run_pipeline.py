import os
import pandas as pd
from pipelines.ingest import generate_raw_data
from pipelines.clean import clean_data
from pipelines.feature_engineering import create_features

def main():
    print("\n=== DemandIQ PIPELINE START ===\n")

    # Step 1 - Ingest
    raw = generate_raw_data()
    os.makedirs("data/raw", exist_ok=True)
    raw.to_csv("data/raw/sales_raw.csv", index=False)
    print(f"Raw      : {raw.shape}")

    # Step 2 - Clean
    cleaned = clean_data(raw)
    os.makedirs("data/processed", exist_ok=True)
    cleaned.to_csv("data/processed/sales_cleaned.csv", index=False)
    print(f"Cleaned  : {cleaned.shape}")

    # Step 3 - Features
    features = create_features(cleaned)
    os.makedirs("data/features", exist_ok=True)
    features.to_csv("data/features/features.csv", index=False)
    print(f"Features : {features.shape}")

    print("\n=== PIPELINE COMPLETE ✅ ===")
    print("\nFINAL SUMMARY")
    print("-" * 30)
    print(f"Raw      : {raw.shape[0]:,} rows, {raw.shape[1]} cols")
    print(f"Cleaned  : {cleaned.shape[0]:,} rows, {cleaned.shape[1]} cols")
    print(f"Features : {features.shape[0]:,} rows, {features.shape[1]} cols")

if __name__ == "__main__":
    main()