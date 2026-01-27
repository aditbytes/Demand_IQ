"""
Reorder Quantity Calculation
Determines optimal reorder quantities and risk levels
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from db.db_utils import get_engine
from inventory.safety_stock import calculate_safety_stock

def get_forecast(store_id, sku, days=7):
    """Get forecasted demand for next N days"""
    engine = get_engine()
    
    query = f"""
    SELECT SUM(predicted_demand) as total_forecast
    FROM forecast
    WHERE store_id = '{store_id}' 
    AND sku = '{sku}'
    AND forecast_date >= CURRENT_DATE
    AND forecast_date < CURRENT_DATE + INTERVAL '{days} days'
    """
    
    result = pd.read_sql(query, engine)
    
    if len(result) == 0 or pd.isna(result['total_forecast'].iloc[0]):
        # Fallback: use recent average
        fallback_query = f"""
        SELECT AVG(units) * {days} as total_forecast
        FROM sales
        WHERE store_id = '{store_id}' AND sku = '{sku}'
        AND date >= CURRENT_DATE - INTERVAL '30 days'
        """
        result = pd.read_sql(fallback_query, engine)
    
    forecast = result['total_forecast'].iloc[0]
    return max(0, forecast) if pd.notna(forecast) else 0

def get_current_stock(store_id, sku):
    """Get current stock level from inventory table"""
    engine = get_engine()
    
    query = f"""
    SELECT current_stock
    FROM inventory
    WHERE store_id = '{store_id}' AND sku = '{sku}'
    """
    
    result = pd.read_sql(query, engine)
    
    if len(result) == 0:
        return 0
    
    return result['current_stock'].iloc[0]

def calculate_reorder_qty(store_id, sku, forecast_days=7):
    """
    Calculate reorder quantity using formula:
    Reorder Qty = Forecast + Safety Stock - Current Stock
    """
    # Get components
    forecast = get_forecast(store_id, sku, days=forecast_days)
    safety_stock = calculate_safety_stock(store_id, sku)
    current_stock = get_current_stock(store_id, sku)
    
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
    
    engine = get_engine()
    
    # Get all items from inventory
    inventory_df = pd.read_sql("SELECT store_id, sku FROM inventory", engine)
    
    print(f"\nGenerating recommendations for {len(inventory_df)} items...")
    
    recommendations = []
    
    for idx, row in inventory_df.iterrows():
        store_id = row['store_id']
        sku = row['sku']
        
        # Calculate reorder quantity
        reorder_info = calculate_reorder_qty(store_id, sku)
        
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
        
        if (idx + 1) % 100 == 0:
            print(f"  Processed {idx + 1}/{len(inventory_df)} items...")
    
    # Convert to DataFrame
    recommendations_df = pd.DataFrame(recommendations)
    
    # Save to CSV
    output_path = Path('inventory/reorder_recommendations.csv')
    recommendations_df.to_csv(output_path, index=False)
    
    # Load to database
    print("\nLoading recommendations to database...")
    recommendations_df.to_sql(
        'reorders',
        engine,
        if_exists='replace',
        index=False
    )
    
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
    print("✓ Loaded to 'reorders' table")
    print("=" * 60)
    
    return recommendations_df

if __name__ == '__main__':
    generate_reorder_recommendations()
