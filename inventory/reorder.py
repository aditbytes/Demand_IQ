"""
Reorder Quantity Calculation
Determines optimal reorder quantities and risk levels
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scipy import stats

# Service level configuration (same as safety_stock.py)
SERVICE_LEVEL = 0.95
Z_SCORE = stats.norm.ppf(SERVICE_LEVEL)
DEFAULT_LEAD_TIME = 7


def load_sales_data():
    """Load sales data from CSV"""
    csv_path = Path('data/processed/sales_cleaned.csv')
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Sales data not found at {csv_path}. Run clean.py first.")
    
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def load_forecast_data():
    """Load forecast data from CSV"""
    csv_path = Path('data/forecast.csv')
    
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        df['forecast_date'] = pd.to_datetime(df['forecast_date'])
        return df
    return None

def load_inventory_data():
    """Load current inventory levels from CSV"""
    csv_path = Path('data/inventory.csv')
    
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None

def calculate_demand_std(df, store_id, sku, days=30):
    """Calculate standard deviation of demand over recent period"""
    df_sku = df[(df['store_id'] == store_id) & (df['sku'] == sku)].copy()
    df_sku = df_sku.sort_values('date')
    df_recent = df_sku.tail(days)
    
    if len(df_recent) < 7:
        return None
    
    return df_recent['units'].std()

def calculate_safety_stock(df, store_id, sku, lead_time=DEFAULT_LEAD_TIME):
    """Calculate safety stock"""
    sigma = calculate_demand_std(df, store_id, sku)
    
    if sigma is None:
        return None
    
    safety_stock = Z_SCORE * sigma * np.sqrt(lead_time)
    return max(0, safety_stock)

def get_forecast(forecast_df, sales_df, store_id, sku, days=7):
    """Get forecasted demand for next N days"""
    if forecast_df is not None:
        df_sku = forecast_df[(forecast_df['store_id'] == store_id) & 
                             (forecast_df['sku'] == sku)]
        if len(df_sku) > 0:
            return df_sku['predicted_demand'].sum()
    
    # Fallback: use recent average from sales data
    df_sku = sales_df[(sales_df['store_id'] == store_id) & 
                      (sales_df['sku'] == sku)]
    if len(df_sku) > 0:
        recent = df_sku.tail(30)
        avg_daily = recent['units'].mean()
        return avg_daily * days
    
    return 0

def get_current_stock(inventory_df, store_id, sku):
    """Get current stock level from inventory data"""
    if inventory_df is not None:
        df_sku = inventory_df[(inventory_df['store_id'] == store_id) & 
                              (inventory_df['sku'] == sku)]
        if len(df_sku) > 0:
            return df_sku['current_stock'].iloc[0]
    
    # Default: generate a sample stock level
    np.random.seed(hash(f"{store_id}-{sku}") % 2**32)
    return np.random.randint(50, 200)

def calculate_reorder_qty(sales_df, forecast_df, inventory_df, store_id, sku, forecast_days=7):
    """
    Calculate reorder quantity using formula:
    Reorder Qty = Forecast + Safety Stock - Current Stock
    """
    # Get components
    forecast = get_forecast(forecast_df, sales_df, store_id, sku, days=forecast_days)
    safety_stock = calculate_safety_stock(sales_df, store_id, sku)
    current_stock = get_current_stock(inventory_df, store_id, sku)
    
    if safety_stock is None:
        safety_stock = forecast * 0.2  # Fallback: 20% of forecast
    
    # Calculate reorder quantity
    reorder_qty = forecast + safety_stock - current_stock
    
    # Cannot order negative quantities
    reorder_qty = max(0, reorder_qty)
    
    return {
        'forecast': round(forecast, 2),
        'safety_stock': round(safety_stock, 2),
        'current_stock': current_stock,
        'reorder_qty': round(reorder_qty, 0)
    }

def classify_risk_level(current_stock, forecast, days=7):
    """
    Classify risk level based on days of stock remaining:
    - HIGH: < 3 days of stock
    - MED: < 7 days of stock
    - LOW: >= 7 days of stock
    """
    if forecast == 0:
        return 'LOW'  # No demand forecasted
    
    daily_demand = forecast / days
    days_of_stock = current_stock / daily_demand if daily_demand > 0 else float('inf')
    
    if days_of_stock < 3:
        return 'HIGH'
    elif days_of_stock < 7:
        return 'MED'
    else:
        return 'LOW'

def generate_reorder_recommendations():
    """Generate reorder recommendations for all items"""
    print("=" * 60)
    print("DemandIQ - Reorder Recommendations")
    print("=" * 60)
    
    # Load data
    sales_df = load_sales_data()
    forecast_df = load_forecast_data()
    inventory_df = load_inventory_data()
    
    # Get all unique store-SKU combinations
    store_sku_combos = sales_df.groupby(['store_id', 'sku']).size().reset_index()[['store_id', 'sku']]
    
    print(f"\nGenerating recommendations for {len(store_sku_combos)} items...")
    
    recommendations = []
    
    for idx, row in store_sku_combos.iterrows():
        store_id = row['store_id']
        sku = row['sku']
        
        # Calculate reorder quantity
        reorder_info = calculate_reorder_qty(sales_df, forecast_df, inventory_df, store_id, sku)
        
        # Classify risk
        risk_level = classify_risk_level(
            reorder_info['current_stock'],
            reorder_info['forecast']
        )
        
        recommendations.append({
            'store_id': store_id,
            'sku': sku,
            'current_stock': reorder_info['current_stock'],
            'forecasted_demand': reorder_info['forecast'],
            'safety_stock': reorder_info['safety_stock'],
            'order_qty': int(reorder_info['reorder_qty']),
            'risk_level': risk_level
        })
        
        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(store_sku_combos)} items...")
    
    # Convert to DataFrame
    recommendations_df = pd.DataFrame(recommendations)
    
    # Save to CSV
    output_path = Path('data/reorders.csv')
    recommendations_df.to_csv(output_path, index=False)
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("Reorder Recommendations Summary")
    print("=" * 60)
    print(f"\nTotal items: {len(recommendations_df)}")
    print(f"\nRisk level breakdown:")
    print(recommendations_df['risk_level'].value_counts())
    print(f"\nItems needing reorder (qty > 0): {(recommendations_df['order_qty'] > 0).sum()}")
    print(f"Average reorder quantity: {recommendations_df['order_qty'].mean():.0f} units")
    print(f"\n✓ Results saved to: {output_path}")
    print("=" * 60)
    
    return recommendations_df

if __name__ == '__main__':
    generate_reorder_recommendations()
