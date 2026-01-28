"""
Feature Engineering Pipeline
Creates lag features, rolling statistics, and calendar features for ML models
"""
import pandas as pd
import numpy as np
from pathlib import Path


def load_sales_from_csv():
    """Load cleaned sales data from CSV"""
    print("Loading sales data from CSV...")
    
    csv_path = Path('data/processed/sales_cleaned.csv')
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Sales data not found at {csv_path}. Run clean.py first.")
    
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort for proper lag/rolling calculations
    df = df.sort_values(['store_id', 'sku', 'date'])
    
    print(f"  Loaded {len(df):,} sales records")
    return df

def create_lag_features(df, lag_days=[7, 14, 28]):
    """Create lag features for each SKU"""
    print(f"\nCreating lag features: {lag_days}")
    
    for lag in lag_days:
        df[f'lag{lag}'] = df.groupby(['store_id', 'sku'])['units'].shift(lag)
    
    return df

def create_rolling_features(df, windows=[7, 30]):
    """Create rolling mean and std features"""
    print(f"Creating rolling features: windows={windows}")
    
    for window in windows:
        # Rolling mean
        df[f'rolling{window}_mean'] = (
            df.groupby(['store_id', 'sku'])['units']
            .transform(lambda x: x.rolling(window=window, min_periods=1).mean())
        )
        
        # Rolling std
        df[f'rolling{window}_std'] = (
            df.groupby(['store_id', 'sku'])['units']
            .transform(lambda x: x.rolling(window=window, min_periods=1).std())
        )
    
    return df

def create_price_features(df):
    """Create price change features"""
    print("Creating price features...")
    
    # Price change from previous day
    df['price_change'] = (
        df.groupby(['store_id', 'sku'])['price']
        .diff()
    )
    
    return df

def create_calendar_features(df):
    """Create calendar-based features"""
    print("Creating calendar features...")
    
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['day_of_month'] = df['date'].dt.day
    df['week_of_year'] = df['date'].dt.isocalendar().week
    
    # Simple holiday detection (can be enhanced with actual holiday calendar)
    df['is_holiday'] = (
        (df['date'].dt.month == 12) & (df['date'].dt.day == 25) |  # Christmas
        (df['date'].dt.month == 1) & (df['date'].dt.day == 1) |     # New Year
        (df['date'].dt.month == 7) & (df['date'].dt.day == 4) |     # July 4th
        (df['date'].dt.month == 11) & (df['date'].dt.day >= 22) & (df['date'].dt.day <= 28)  # Thanksgiving week
    )
    
    # SNAP (Supplemental Nutrition Assistance Program) - placeholder
    df['is_snap'] = False  # Would need actual SNAP calendar
    
    return df

def engineer_features():
    """Main feature engineering pipeline"""
    print("=" * 60)
    print("DemandIQ - Feature Engineering Pipeline")
    print("=" * 60)
    
    # Load sales data from CSV
    df = load_sales_from_csv()
    
    # Create lag features
    df = create_lag_features(df, lag_days=[7, 14, 28])
    
    # Create rolling features
    df = create_rolling_features(df, windows=[7, 30])
    
    # Create price features
    df = create_price_features(df)
    
    # Create calendar features
    df = create_calendar_features(df)
    
    # Drop rows with NaN in critical features (due to lags/rolling windows)
    print(f"\nRows before dropping NaN: {len(df):,}")
    df_features = df.dropna(subset=['lag7', 'lag14'])
    print(f"Rows after dropping NaN: {len(df_features):,}")
    
    # Select feature columns
    feature_cols = [
        'date', 'store_id', 'sku', 'units',
        'lag7', 'lag14', 'lag28',
        'rolling7_mean', 'rolling7_std',
        'rolling30_mean', 'rolling30_std',
        'price', 'price_change', 'promo',
        'day_of_week', 'month', 'is_holiday', 'is_snap'
    ]
    
    df_final = df_features[feature_cols].copy()
    
    # Save to CSV file
    features_dir = Path('data/features')
    features_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = features_dir / 'features.csv'
    df_final.to_csv(output_path, index=False)
    print(f"\n✓ Saved features to: {output_path}")
    
    print("\n" + "=" * 60)
    print("✓ Feature engineering complete!")
    print("=" * 60)
    
    return df_final

if __name__ == '__main__':
    engineer_features()
