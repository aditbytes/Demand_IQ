"""
Data Cleaning Pipeline
Transforms raw M5 data into cleaned format and loads into PostgreSQL
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from db.db_utils import get_engine

def load_raw_data():
    """Load raw M5 datasets"""
    print("Loading raw data files...")
    
    sales_df = pd.read_csv('data/raw/sales.csv')
    calendar_df = pd.read_csv('data/raw/calendar.csv')
    prices_df = pd.read_csv('data/raw/prices.csv')
    
    print(f"  Sales shape: {sales_df.shape}")
    print(f"  Calendar shape: {calendar_df.shape}")
    print(f"  Prices shape: {prices_df.shape}")
    
    return sales_df, calendar_df, prices_df

def transform_sales_data(sales_df, calendar_df, prices_df):
    """Transform wide sales data to long format with calendar and price info"""
    print("\nTransforming sales data to long format...")
    
    # Get product columns (id, item_id, dept_id, cat_id, store_id, state_id)
    id_cols = ['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id']
    
    # Melt sales data from wide to long
    sales_long = sales_df.melt(
        id_vars=id_cols,
        var_name='d',
        value_name='units'
    )
    
    print(f"  Sales long format shape: {sales_long.shape}")
    
    # Merge with calendar to get actual dates
    sales_long = sales_long.merge(
        calendar_df[['d', 'date', 'event_name_1', 'snap_CA', 'snap_TX', 'snap_WI']],
        on='d',
        how='left'
    )
    
    # Create SKU (Stock Keeping Unit) from item_id
    sales_long['sku'] = sales_long['item_id']
    
    # Merge with prices
    sales_long = sales_long.merge(
        prices_df,
        on=['store_id', 'item_id', 'wm_yr_wk'],
        how='left'
    ) if 'wm_yr_wk' in calendar_df.columns else sales_long
    
    # For simplicity, merge prices based on store_id and item_id only
    # (In production, would need proper week matching)
    price_avg = prices_df.groupby(['store_id', 'item_id'])['sell_price'].mean().reset_index()
    price_avg.columns = ['store_id', 'item_id', 'price']
    
    sales_long = sales_long.merge(
        price_avg,
        left_on=['store_id', 'item_id'],
        right_on=['store_id', 'item_id'],
        how='left'
    )
    
    # Create promo flag (if event exists)
    sales_long['promo'] = sales_long['event_name_1'].notna()
    
    # Select final columns
    final_df = sales_long[['date', 'store_id', 'sku', 'units', 'price', 'promo']].copy()
    
    # Handle missing values
    final_df['units'] = final_df['units'].fillna(0).astype(int)
    final_df['price'] = final_df['price'].fillna(final_df['price'].median())
    final_df['promo'] = final_df['promo'].fillna(False)
    
    # Convert date to datetime
    final_df['date'] = pd.to_datetime(final_df['date'])
    
    print(f"✓ Final cleaned data shape: {final_df.shape}")
    
    return final_df

def load_to_database(df, table_name='sales', batch_size=10000):
    """Load cleaned data to PostgreSQL"""
    print(f"\nLoading data to PostgreSQL table '{table_name}'...")
    
    engine = get_engine()
    
    # Load in batches
    total_rows = len(df)
    for i in range(0, total_rows, batch_size):
        batch = df.iloc[i:i+batch_size]
        batch.to_sql(
            table_name,
            engine,
            if_exists='append' if i > 0 else 'replace',
            index=False,
            method='multi'
        )
        print(f"  Loaded {min(i+batch_size, total_rows):,} / {total_rows:,} rows")
    
    print(f"✓ Successfully loaded {total_rows:,} rows to '{table_name}' table")

def clean_data():
    """Main cleaning pipeline"""
    print("=" * 60)
    print("DemandIQ - Data Cleaning Pipeline")
    print("=" * 60)
    
    # Load raw data
    sales_df, calendar_df, prices_df = load_raw_data()
    
    # Transform to cleaned format
    cleaned_df = transform_sales_data(sales_df, calendar_df, prices_df)
    
    # Save processed data locally
    processed_dir = Path('data/processed')
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = processed_dir / 'sales_cleaned.csv'
    cleaned_df.to_csv(output_path, index=False)
    print(f"\n✓ Saved cleaned data to: {output_path}")
    
    # Load to database
    load_to_database(cleaned_df, table_name='sales')
    
    print("\n" + "=" * 60)
    print("✓ Data cleaning complete!")
    print("=" * 60)

if __name__ == '__main__':
    clean_data()
