"""
Safety Stock Calculation
Implements safety stock formula based on demand variability and lead time
"""
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats


# Service level configuration
SERVICE_LEVEL = 0.95  # 95% service level
Z_SCORE = stats.norm.ppf(SERVICE_LEVEL)  # ~1.65

# Default lead time in days
DEFAULT_LEAD_TIME = 7


def load_sales_data():
    """Load sales data from CSV"""
    csv_path = Path('data/processed/sales_cleaned.csv')
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Sales data not found at {csv_path}. Run clean.py first.")
    
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def calculate_demand_std(df, store_id, sku, days=30):
    """Calculate standard deviation of demand over recent period"""
    df_sku = df[(df['store_id'] == store_id) & (df['sku'] == sku)].copy()
    df_sku = df_sku.sort_values('date')
    
    # Get most recent N days
    df_recent = df_sku.tail(days)
    
    if len(df_recent) < 7:  # Insufficient data
        return None
    
    return df_recent['units'].std()

def calculate_safety_stock(df, store_id, sku, lead_time=DEFAULT_LEAD_TIME):
    """
    Calculate safety stock using the formula:
    Safety Stock = Z × σ × √(lead_time)
    
    Where:
    - Z = Z-score for desired service level (1.65 for 95%)
    - σ = standard deviation of demand
    - lead_time = days from order to delivery
    """
    # Get demand standard deviation
    sigma = calculate_demand_std(df, store_id, sku)
    
    if sigma is None:
        return None
    
    # Safety stock formula
    safety_stock = Z_SCORE * sigma * np.sqrt(lead_time)
    
    return max(0, safety_stock)  # Cannot be negative

def calculate_all_safety_stocks():
    """Calculate safety stock for all store-SKU combinations"""
    print("=" * 60)
    print("DemandIQ - Safety Stock Calculation")
    print("=" * 60)
    print(f"Service Level: {SERVICE_LEVEL*100:.0f}%")
    print(f"Z-Score: {Z_SCORE:.2f}")
    print(f"Default Lead Time: {DEFAULT_LEAD_TIME} days")
    
    # Load sales data
    df = load_sales_data()
    
    # Get all unique store-SKU combinations
    store_sku_combos = df.groupby(['store_id', 'sku']).size().reset_index()[['store_id', 'sku']]
    
    print(f"\nCalculating safety stock for {len(store_sku_combos)} items...")
    
    results = []
    
    for idx, row in store_sku_combos.iterrows():
        store_id = row['store_id']
        sku = row['sku']
        lead_time = DEFAULT_LEAD_TIME
        
        safety_stock = calculate_safety_stock(df, store_id, sku, lead_time)
        
        if safety_stock is not None:
            results.append({
                'store_id': store_id,
                'sku': sku,
                'lead_time': lead_time,
                'safety_stock': round(safety_stock, 2)
            })
            
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(store_sku_combos)} items...")
    
    # Save results
    results_df = pd.DataFrame(results)
    output_path = Path('inventory/safety_stock_results.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)
    
    print("\n" + "=" * 60)
    print(f"✓ Safety stock calculation complete!")
    print(f"  Calculated for {len(results_df)} items")
    if len(results_df) > 0:
        print(f"  Average safety stock: {results_df['safety_stock'].mean():.2f} units")
    print(f"  Results saved to: {output_path}")
    print("=" * 60)
    
    return results_df

if __name__ == '__main__':
    calculate_all_safety_stocks()
