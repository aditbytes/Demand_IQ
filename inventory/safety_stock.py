"""
Safety Stock Calculation
Implements safety stock formula based on demand variability and lead time
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from db.db_utils import get_engine
from scipy import stats

# Service level configuration
SERVICE_LEVEL = 0.95  # 95% service level
Z_SCORE = stats.norm.ppf(SERVICE_LEVEL)  # ~1.65

def calculate_demand_std(store_id, sku, days=30):
    """Calculate standard deviation of demand over recent period"""
    engine = get_engine()
    
    query = f"""
    SELECT units
    FROM sales
    WHERE store_id = '{store_id}' AND sku = '{sku}'
    ORDER BY date DESC
    LIMIT {days}
    """
    
    df = pd.read_sql(query, engine)
    
    if len(df) < 7:  # Insufficient data
        return None
    
    return df['units'].std()

def calculate_safety_stock(store_id, sku, lead_time=7):
    """
    Calculate safety stock using the formula:
    Safety Stock = Z × σ × √(lead_time)
    
    Where:
    - Z = Z-score for desired service level (1.65 for 95%)
    - σ = standard deviation of demand
    - lead_time = days from order to delivery
    """
    # Get demand standard deviation
    sigma = calculate_demand_std(store_id, sku)
    
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
    
    engine = get_engine()
    
    # Get all unique store-SKU combinations from inventory
    query = """
    SELECT DISTINCT store_id, sku, lead_time
    FROM inventory
    """
    
    inventory_df = pd.read_sql(query, engine)
    
    if len(inventory_df) == 0:
        print("\n✗ No inventory data found. Please populate inventory table first.")
        return
    
    print(f"\nCalculating safety stock for {len(inventory_df)} items...")
    
    results = []
    
    for idx, row in inventory_df.iterrows():
        store_id = row['store_id']
        sku = row['sku']
        lead_time = row['lead_time'] if pd.notna(row['lead_time']) else 7
        
        safety_stock = calculate_safety_stock(store_id, sku, lead_time)
        
        if safety_stock is not None:
            results.append({
                'store_id': store_id,
                'sku': sku,
                'lead_time': lead_time,
                'safety_stock': round(safety_stock, 2)
            })
            
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(inventory_df)} items...")
    
    # Save results
    results_df = pd.DataFrame(results)
    output_path = Path('inventory/safety_stock_results.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)
    
    print("\n" + "=" * 60)
    print(f"✓ Safety stock calculation complete!")
    print(f"  Calculated for {len(results_df)} items")
    print(f"  Average safety stock: {results_df['safety_stock'].mean():.2f} units")
    print(f"  Results saved to: {output_path}")
    print("=" * 60)
    
    return results_df

if __name__ == '__main__':
    calculate_all_safety_stocks()
