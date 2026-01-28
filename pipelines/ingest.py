"""
Data Ingestion / Sample Data Generation
Generates sample retail data for DemandIQ demo
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta


def generate_sample_data():
    """Generate sample retail sales data for demo"""
    print("=" * 60)
    print("DemandIQ - Data Generation Pipeline")
    print("=" * 60)
    
    # Create directories
    raw_dir = Path('data/raw')
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    np.random.seed(42)
    
    # Configuration
    stores = ['CA_1', 'CA_2', 'TX_1', 'TX_2', 'WI_1']
    categories = ['FOODS', 'HOBBIES', 'HOUSEHOLD']
    items_per_category = 10
    days = 365  # 1 year of data
    
    print(f"\nGenerating data for {len(stores)} stores, {len(categories)} categories, {days} days...")
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate calendar data
    print("  Creating calendar.csv...")
    calendar_data = {
        'd': [f'd_{i+1}' for i in range(len(dates))],
        'date': dates.strftime('%Y-%m-%d'),
        'wm_yr_wk': [(d.year * 100 + d.isocalendar()[1]) for d in dates],
        'weekday': [d.strftime('%A') for d in dates],
        'month': [d.month for d in dates],
        'year': [d.year for d in dates],
        'event_name_1': [None] * len(dates),
        'snap_CA': np.random.choice([0, 1], size=len(dates), p=[0.7, 0.3]),
        'snap_TX': np.random.choice([0, 1], size=len(dates), p=[0.7, 0.3]),
        'snap_WI': np.random.choice([0, 1], size=len(dates), p=[0.7, 0.3]),
    }
    
    # Add some events
    event_days = np.random.choice(range(len(dates)), size=30, replace=False)
    events = ['SuperBowl', 'ValentinesDay', 'Easter', 'MothersDay', 'MemorialDay', 
              'FathersDay', 'IndependenceDay', 'LaborDay', 'Halloween', 'Thanksgiving',
              'Christmas', 'NewYear', 'BlackFriday', 'CyberMonday', 'SportingEvent']
    for i, day in enumerate(event_days):
        calendar_data['event_name_1'][day] = events[i % len(events)]
    
    calendar_df = pd.DataFrame(calendar_data)
    calendar_df.to_csv(raw_dir / 'calendar.csv', index=False)
    print(f"    ✓ calendar.csv: {len(calendar_df)} rows")
    
    # Generate sales data (wide format like M5)
    print("  Creating sales.csv...")
    sales_rows = []
    
    for store in stores:
        state = store.split('_')[0]
        for cat_idx, category in enumerate(categories):
            for item_num in range(1, items_per_category + 1):
                item_id = f"{category}_{cat_idx+1}_{item_num:03d}"
                dept_id = f"{category}_{cat_idx+1}"
                
                # Generate row data
                row = {
                    'id': f"{item_id}_{store}_validation",
                    'item_id': item_id,
                    'dept_id': dept_id,
                    'cat_id': category,
                    'store_id': store,
                    'state_id': state,
                }
                
                # Generate sales for each day with seasonal patterns
                base_demand = np.random.randint(5, 50)
                weekly_pattern = [1.0, 0.9, 0.85, 0.8, 1.1, 1.4, 1.3]  # Mon-Sun
                
                for i, d in enumerate(dates):
                    day_col = f'd_{i+1}'
                    seasonal = weekly_pattern[d.weekday()]
                    trend = 1 + 0.001 * i  # Slight upward trend
                    noise = np.random.normal(1, 0.2)
                    sales = max(0, int(base_demand * seasonal * trend * noise))
                    row[day_col] = sales
                
                sales_rows.append(row)
    
    sales_df = pd.DataFrame(sales_rows)
    sales_df.to_csv(raw_dir / 'sales.csv', index=False)
    print(f"    ✓ sales.csv: {len(sales_df)} products × {days} days")
    
    # Generate prices data
    print("  Creating prices.csv...")
    prices_rows = []
    
    weeks = calendar_df['wm_yr_wk'].unique()
    
    for store in stores:
        for cat_idx, category in enumerate(categories):
            for item_num in range(1, items_per_category + 1):
                item_id = f"{category}_{cat_idx+1}_{item_num:03d}"
                base_price = np.random.uniform(1.99, 29.99)
                
                for week in weeks:
                    # Add some price variation
                    price_variation = np.random.choice([1.0, 0.9, 0.95, 1.05], p=[0.7, 0.1, 0.1, 0.1])
                    price = round(base_price * price_variation, 2)
                    
                    prices_rows.append({
                        'store_id': store,
                        'item_id': item_id,
                        'wm_yr_wk': week,
                        'sell_price': price
                    })
    
    prices_df = pd.DataFrame(prices_rows)
    prices_df.to_csv(raw_dir / 'prices.csv', index=False)
    print(f"    ✓ prices.csv: {len(prices_df)} rows")
    
    print("\n" + "=" * 60)
    print("✓ Sample data generation complete!")
    print(f"  Files saved to: {raw_dir.absolute()}")
    print("=" * 60)
    
    return True


def ingest_data():
    """Main ingestion function - generates sample data"""
    return generate_sample_data()


if __name__ == '__main__':
    ingest_data()
