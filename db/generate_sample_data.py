"""
Sample data generator for testing DemandIQ
Populates inventory table with sample stock levels
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from db.db_utils import get_engine

def generate_sample_inventory():
    """Generate sample inventory data for testing"""
    print("=" * 60)
    print("Generating Sample Inventory Data")
    print("=" * 60)
    
    engine = get_engine()
    
    # Get unique store-SKU combinations from sales
    query = """
    SELECT DISTINCT store_id, sku
    FROM sales
    ORDER BY store_id, sku
    LIMIT 100
    """
    
    df = pd.read_sql(query, engine)
    print(f"\nGenerating inventory for {len(df)} store-SKU combinations...")
    
    # Generate random current stock levels
    df['current_stock'] = np.random.randint(10, 200, size=len(df))
    
    # Random lead times (3-14 days)
    df['lead_time'] = np.random.randint(3, 15, size=len(df))
    
    # Load to database
    df.to_sql('inventory', engine, if_exists='replace', index=False)
    
    print(f"✓ Successfully generated inventory for {len(df)} items")
    print(f"  Average stock: {df['current_stock'].mean():.0f} units")
    print(f"  Average lead time: {df['lead_time'].mean():.1f} days")
    print("=" * 60)

if __name__ == '__main__':
    generate_sample_inventory()
