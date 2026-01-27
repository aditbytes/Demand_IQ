"""
Data Ingestion Pipeline
Downloads and prepares Walmart M5 dataset
"""
import os
import requests
import zipfile
from pathlib import Path

# Walmart M5 dataset URLs (Kaggle competition)
DATASET_URLS = {
    'sales': 'https://raw.githubusercontent.com/Mcompetitions/M5-methods/master/Point%20Forecasts/sales_train_validation.csv',
    'calendar': 'https://raw.githubusercontent.com/Mcompetitions/M5-methods/master/Point%20Forecasts/calendar.csv',
    'prices': 'https://raw.githubusercontent.com/Mcompetitions/M5-methods/master/Point%20Forecasts/sell_prices.csv'
}

def download_file(url, destination):
    """Download file from URL to destination"""
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"✓ Downloaded to {destination}")

def ingest_data():
    """Main ingestion function"""
    # Create raw data directory
    raw_dir = Path('data/raw')
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("DemandIQ - Data Ingestion Pipeline")
    print("=" * 60)
    
    # Download each dataset
    for name, url in DATASET_URLS.items():
        destination = raw_dir / f'{name}.csv'
        
        if destination.exists():
            print(f"✓ {name}.csv already exists, skipping...")
        else:
            try:
                download_file(url, destination)
            except Exception as e:
                print(f"✗ Failed to download {name}: {e}")
                print(f"  Please download manually from Kaggle M5 competition:")
                print(f"  https://www.kaggle.com/c/m5-forecasting-accuracy/data")
                return False
    
    print("\n" + "=" * 60)
    print("✓ Data ingestion complete!")
    print(f"  Files saved to: {raw_dir.absolute()}")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    ingest_data()
