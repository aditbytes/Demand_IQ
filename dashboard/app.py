"""
DemandIQ Streamlit Dashboard - Enhanced Version
Store manager interface for demand forecasting and reorder recommendations
"""
import sys
import os

# Add parent directory to path for imports
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Import Telegram notifier
from utils.telegram_notifier import send_reorder_notification

# ============================================================
# DEMO MODE: Using sample data (CSV-based storage)
# ============================================================
DEMO_MODE = True

# Page configuration
st.set_page_config(
    page_title="DemandIQ Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
    }
    .risk-high {
        background-color: #ff4444;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .risk-med {
        background-color: #ffaa00;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .risk-low {
        background-color: #00cc44;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .demo-banner {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .stat-card {
        background: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        border-left: 4px solid #667eea;
    }
    .category-tag {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Enhanced Sample Data - 10 Stores with More Products
# ============================================================

# Store information with location and details
STORE_INFO = {
    'STORE-001': {'name': 'Downtown Central', 'region': 'North', 'type': 'Supermarket', 'size': 'Large'},
    'STORE-002': {'name': 'Westside Mall', 'region': 'West', 'type': 'Hypermarket', 'size': 'Extra Large'},
    'STORE-003': {'name': 'Harbor View', 'region': 'South', 'type': 'Supermarket', 'size': 'Medium'},
    'STORE-004': {'name': 'Tech Park Express', 'region': 'East', 'type': 'Express', 'size': 'Small'},
    'STORE-005': {'name': 'University Square', 'region': 'Central', 'type': 'Supermarket', 'size': 'Medium'},
    'STORE-006': {'name': 'Airport Terminal', 'region': 'North', 'type': 'Express', 'size': 'Small'},
    'STORE-007': {'name': 'Riverside Plaza', 'region': 'West', 'type': 'Supermarket', 'size': 'Large'},
    'STORE-008': {'name': 'Industrial Zone', 'region': 'South', 'type': 'Warehouse', 'size': 'Extra Large'},
    'STORE-009': {'name': 'Suburban Heights', 'region': 'East', 'type': 'Supermarket', 'size': 'Large'},
    'STORE-010': {'name': 'City Center', 'region': 'Central', 'type': 'Hypermarket', 'size': 'Extra Large'},
}

# Product catalog with categories, prices, and supplier info
PRODUCT_CATALOG = {
    # Dairy
    'SKU-MILK-001': {'name': 'Fresh Whole Milk 1L', 'category': 'Dairy', 'unit_price': 3.49, 'cost': 2.10, 'supplier': 'DairyFarm Co.', 'lead_time': 2},
    'SKU-MILK-002': {'name': 'Skim Milk 1L', 'category': 'Dairy', 'unit_price': 3.29, 'cost': 1.95, 'supplier': 'DairyFarm Co.', 'lead_time': 2},
    'SKU-BUTTER-001': {'name': 'Salted Butter 500g', 'category': 'Dairy', 'unit_price': 5.99, 'cost': 3.60, 'supplier': 'DairyFarm Co.', 'lead_time': 3},
    'SKU-CHEESE-001': {'name': 'Cheddar Cheese 200g', 'category': 'Dairy', 'unit_price': 4.49, 'cost': 2.70, 'supplier': 'CheeseWorld', 'lead_time': 4},
    'SKU-YOGURT-001': {'name': 'Greek Yogurt 500g', 'category': 'Dairy', 'unit_price': 4.99, 'cost': 3.00, 'supplier': 'DairyFarm Co.', 'lead_time': 2},
    # Bakery
    'SKU-BREAD-001': {'name': 'White Bread Loaf', 'category': 'Bakery', 'unit_price': 2.99, 'cost': 1.20, 'supplier': 'LocalBakery', 'lead_time': 1},
    'SKU-BREAD-002': {'name': 'Whole Wheat Bread', 'category': 'Bakery', 'unit_price': 3.49, 'cost': 1.50, 'supplier': 'LocalBakery', 'lead_time': 1},
    'SKU-CROISS-001': {'name': 'Butter Croissants 4pk', 'category': 'Bakery', 'unit_price': 4.99, 'cost': 2.50, 'supplier': 'LocalBakery', 'lead_time': 1},
    # Eggs & Protein
    'SKU-EGGS-001': {'name': 'Free-Range Eggs 12pk', 'category': 'Eggs', 'unit_price': 5.99, 'cost': 3.60, 'supplier': 'FarmFresh', 'lead_time': 2},
    'SKU-EGGS-002': {'name': 'Organic Eggs 6pk', 'category': 'Eggs', 'unit_price': 4.49, 'cost': 2.70, 'supplier': 'FarmFresh', 'lead_time': 2},
    'SKU-BACON-001': {'name': 'Smoked Bacon 250g', 'category': 'Meat', 'unit_price': 6.99, 'cost': 4.20, 'supplier': 'MeatMasters', 'lead_time': 3},
    'SKU-SAUSAGE-001': {'name': 'Pork Sausages 500g', 'category': 'Meat', 'unit_price': 7.49, 'cost': 4.50, 'supplier': 'MeatMasters', 'lead_time': 3},
    # Beverages
    'SKU-JUICE-001': {'name': 'Orange Juice 1L', 'category': 'Beverages', 'unit_price': 3.99, 'cost': 2.40, 'supplier': 'JuiceCo', 'lead_time': 3},
    'SKU-JUICE-002': {'name': 'Apple Juice 1L', 'category': 'Beverages', 'unit_price': 3.79, 'cost': 2.25, 'supplier': 'JuiceCo', 'lead_time': 3},
    'SKU-COFFEE-001': {'name': 'Premium Coffee 250g', 'category': 'Beverages', 'unit_price': 8.99, 'cost': 5.40, 'supplier': 'CoffeeRoasters', 'lead_time': 5},
    'SKU-TEA-001': {'name': 'Green Tea 50 bags', 'category': 'Beverages', 'unit_price': 4.99, 'cost': 3.00, 'supplier': 'TeaImports', 'lead_time': 7},
    # Breakfast & Cereals
    'SKU-CEREAL-001': {'name': 'Cornflakes 500g', 'category': 'Cereals', 'unit_price': 4.49, 'cost': 2.70, 'supplier': 'CerealCorp', 'lead_time': 5},
    'SKU-CEREAL-002': {'name': 'Muesli 750g', 'category': 'Cereals', 'unit_price': 6.99, 'cost': 4.20, 'supplier': 'CerealCorp', 'lead_time': 5},
    'SKU-OATS-001': {'name': 'Rolled Oats 1kg', 'category': 'Cereals', 'unit_price': 3.99, 'cost': 2.40, 'supplier': 'CerealCorp', 'lead_time': 5},
    # Snacks
    'SKU-CHIPS-001': {'name': 'Potato Chips 200g', 'category': 'Snacks', 'unit_price': 3.49, 'cost': 1.75, 'supplier': 'SnackFactory', 'lead_time': 7},
    'SKU-CHOCO-001': {'name': 'Dark Chocolate 100g', 'category': 'Snacks', 'unit_price': 3.99, 'cost': 2.00, 'supplier': 'ChocoDelights', 'lead_time': 10},
    # Frozen
    'SKU-ICECREAM-001': {'name': 'Vanilla Ice Cream 1L', 'category': 'Frozen', 'unit_price': 6.49, 'cost': 3.90, 'supplier': 'FrozenFoods', 'lead_time': 3},
    'SKU-PIZZA-001': {'name': 'Frozen Pizza Margherita', 'category': 'Frozen', 'unit_price': 7.99, 'cost': 4.80, 'supplier': 'FrozenFoods', 'lead_time': 3},
}

# SKUs available at each store (larger inventory)
SAMPLE_SKUS = {
    'STORE-001': ['SKU-MILK-001', 'SKU-MILK-002', 'SKU-BREAD-001', 'SKU-EGGS-001', 'SKU-BUTTER-001', 
                  'SKU-CHEESE-001', 'SKU-YOGURT-001', 'SKU-JUICE-001', 'SKU-COFFEE-001', 'SKU-CEREAL-001'],
    'STORE-002': ['SKU-MILK-001', 'SKU-BREAD-001', 'SKU-BREAD-002', 'SKU-JUICE-001', 'SKU-JUICE-002',
                  'SKU-CEREAL-001', 'SKU-CEREAL-002', 'SKU-COFFEE-001', 'SKU-TEA-001', 'SKU-CHIPS-001',
                  'SKU-ICECREAM-001', 'SKU-PIZZA-001'],
    'STORE-003': ['SKU-MILK-001', 'SKU-EGGS-001', 'SKU-EGGS-002', 'SKU-BUTTER-001', 'SKU-BACON-001', 
                  'SKU-SAUSAGE-001', 'SKU-CHEESE-001', 'SKU-CROISS-001'],
    'STORE-004': ['SKU-BREAD-001', 'SKU-MILK-001', 'SKU-COFFEE-001', 'SKU-CROISS-001', 'SKU-JUICE-001'],
    'STORE-005': ['SKU-MILK-001', 'SKU-MILK-002', 'SKU-BREAD-001', 'SKU-EGGS-001', 'SKU-CEREAL-001',
                  'SKU-CEREAL-002', 'SKU-COFFEE-001', 'SKU-TEA-001', 'SKU-OATS-001'],
    'STORE-006': ['SKU-BREAD-001', 'SKU-COFFEE-001', 'SKU-JUICE-001', 'SKU-CHIPS-001', 'SKU-CHOCO-001'],
    'STORE-007': ['SKU-MILK-001', 'SKU-BREAD-001', 'SKU-BREAD-002', 'SKU-EGGS-001', 'SKU-BUTTER-001',
                  'SKU-YOGURT-001', 'SKU-JUICE-001', 'SKU-JUICE-002', 'SKU-ICECREAM-001'],
    'STORE-008': ['SKU-MILK-001', 'SKU-MILK-002', 'SKU-BREAD-001', 'SKU-BREAD-002', 'SKU-EGGS-001',
                  'SKU-EGGS-002', 'SKU-BUTTER-001', 'SKU-CHEESE-001', 'SKU-BACON-001', 'SKU-SAUSAGE-001',
                  'SKU-CEREAL-001', 'SKU-CEREAL-002', 'SKU-PIZZA-001', 'SKU-ICECREAM-001'],
    'STORE-009': ['SKU-MILK-001', 'SKU-BREAD-001', 'SKU-EGGS-001', 'SKU-CHEESE-001', 'SKU-YOGURT-001',
                  'SKU-JUICE-001', 'SKU-COFFEE-001', 'SKU-OATS-001', 'SKU-CHOCO-001'],
    'STORE-010': ['SKU-MILK-001', 'SKU-MILK-002', 'SKU-BREAD-001', 'SKU-BREAD-002', 'SKU-CROISS-001',
                  'SKU-EGGS-001', 'SKU-EGGS-002', 'SKU-BUTTER-001', 'SKU-CHEESE-001', 'SKU-YOGURT-001',
                  'SKU-BACON-001', 'SKU-SAUSAGE-001', 'SKU-JUICE-001', 'SKU-JUICE-002', 'SKU-COFFEE-001',
                  'SKU-TEA-001', 'SKU-CEREAL-001', 'SKU-OATS-001', 'SKU-ICECREAM-001', 'SKU-PIZZA-001'],
}

SAMPLE_STORES = list(STORE_INFO.keys())

# ============================================================
# Data Loading Functions
# ============================================================

@st.cache_data(ttl=300)
def load_stores():
    """Load available stores with info"""
    return SAMPLE_STORES

@st.cache_data(ttl=300)
def load_store_info(store_id):
    """Get store information"""
    return STORE_INFO.get(store_id, {})

@st.cache_data(ttl=300)
def load_skus(store_id=None):
    """Load available SKUs for a store"""
    if store_id and store_id in SAMPLE_SKUS:
        return SAMPLE_SKUS[store_id]
    all_skus = set()
    for skus in SAMPLE_SKUS.values():
        all_skus.update(skus)
    return sorted(list(all_skus))

@st.cache_data(ttl=300)
def load_product_info(sku):
    """Get product information"""
    return PRODUCT_CATALOG.get(sku, {})

@st.cache_data(ttl=60)
def load_sales_history(store_id, sku, days=180):
    """Generate sample sales history (extended to 180 days)"""
    np.random.seed(hash(f"{store_id}-{sku}") % 2**32)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Base demand varies by store size
    store_info = STORE_INFO.get(store_id, {})
    size_multiplier = {'Small': 0.5, 'Medium': 1.0, 'Large': 1.5, 'Extra Large': 2.0}.get(store_info.get('size', 'Medium'), 1.0)
    base_demand = int(np.random.randint(30, 70) * size_multiplier)
    
    # Weekly pattern (Mon-Sun)
    weekly_pattern = [1.2, 1.0, 0.9, 0.85, 1.1, 1.4, 1.3]
    
    # Monthly seasonality
    monthly_seasonality = [0.9, 0.85, 0.95, 1.0, 1.05, 1.1, 1.15, 1.1, 1.0, 1.05, 1.1, 1.2]
    
    product_info = PRODUCT_CATALOG.get(sku, {})
    unit_price = product_info.get('unit_price', 5.00)
    
    records = []
    for d in dates:
        weekly_factor = weekly_pattern[d.weekday()]
        monthly_factor = monthly_seasonality[d.month - 1]
        noise = np.random.normal(0, base_demand * 0.15)
        
        units = max(0, int(base_demand * weekly_factor * monthly_factor + noise))
        
        # Occasional promotions
        promo = np.random.choice([True, False], p=[0.12, 0.88])
        promo_discount = np.random.uniform(0.1, 0.3) if promo else 0
        actual_price = round(unit_price * (1 - promo_discount), 2)
        
        # Promo boosts sales
        if promo:
            units = int(units * np.random.uniform(1.3, 1.8))
        
        records.append({
            'date': d,
            'units': units,
            'price': actual_price,
            'revenue': round(units * actual_price, 2),
            'promo': promo
        })
    
    return pd.DataFrame(records)

@st.cache_data(ttl=60)
def load_forecast(store_id, sku, days=14):
    """Generate sample forecast data (14 days)"""
    np.random.seed(hash(f"{store_id}-{sku}-forecast") % 2**32)
    
    dates = pd.date_range(start=datetime.now(), periods=days, freq='D')
    
    store_info = STORE_INFO.get(store_id, {})
    size_multiplier = {'Small': 0.5, 'Medium': 1.0, 'Large': 1.5, 'Extra Large': 2.0}.get(store_info.get('size', 'Medium'), 1.0)
    base_demand = int(np.random.randint(30, 70) * size_multiplier)
    
    weekly_pattern = [1.2, 1.0, 0.9, 0.85, 1.1, 1.4, 1.3]
    
    records = []
    for i, d in enumerate(dates):
        seasonal_factor = weekly_pattern[d.weekday()]
        # Add uncertainty that increases with forecast horizon
        uncertainty = 1 + i * 0.02
        pred = base_demand * seasonal_factor * np.random.uniform(0.95 / uncertainty, 1.05 * uncertainty)
        
        # Confidence interval
        lower = pred * 0.8
        upper = pred * 1.2
        
        records.append({
            'date': d,
            'predicted_demand': round(pred, 1),
            'lower_bound': round(lower, 1),
            'upper_bound': round(upper, 1)
        })
    
    return pd.DataFrame(records)

@st.cache_data(ttl=60)
def load_reorder_info(store_id, sku):
    """Generate sample reorder recommendation with extended data"""
    np.random.seed(hash(f"{store_id}-{sku}-reorder") % 2**32)
    
    product_info = PRODUCT_CATALOG.get(sku, {})
    store_info = STORE_INFO.get(store_id, {})
    
    size_multiplier = {'Small': 0.5, 'Medium': 1.0, 'Large': 1.5, 'Extra Large': 2.0}.get(store_info.get('size', 'Medium'), 1.0)
    
    forecasted_demand = int(np.random.randint(150, 400) * size_multiplier)
    safety_stock = int(forecasted_demand * 0.2)
    current_stock = np.random.randint(30, int(forecasted_demand * 1.2))
    
    order_qty = max(0, forecasted_demand + safety_stock - current_stock)
    
    stock_ratio = current_stock / (forecasted_demand + safety_stock) if (forecasted_demand + safety_stock) > 0 else 1
    if stock_ratio < 0.4:
        risk_level = 'HIGH'
    elif stock_ratio < 0.7:
        risk_level = 'MED'
    else:
        risk_level = 'LOW'
    
    # Calculate days of stock remaining
    daily_demand = forecasted_demand / 7
    days_of_stock = current_stock / daily_demand if daily_demand > 0 else 99
    
    # Calculate financials
    unit_cost = product_info.get('cost', 3.00)
    unit_price = product_info.get('unit_price', 5.00)
    
    return pd.Series({
        'current_stock': current_stock,
        'forecasted_demand': forecasted_demand,
        'safety_stock': safety_stock,
        'order_qty': order_qty,
        'risk_level': risk_level,
        'days_of_stock': round(days_of_stock, 1),
        'lead_time': product_info.get('lead_time', 3),
        'supplier': product_info.get('supplier', 'Unknown'),
        'order_value': round(order_qty * unit_cost, 2),
        'potential_revenue': round(order_qty * unit_price, 2),
        'profit_margin': round((unit_price - unit_cost) / unit_price * 100, 1)
    })

@st.cache_data(ttl=60)
def load_all_inventory():
    """Load inventory status for all stores"""
    inventory = []
    for store_id in SAMPLE_STORES:
        for sku in SAMPLE_SKUS.get(store_id, []):
            info = load_reorder_info(store_id, sku)
            product = PRODUCT_CATALOG.get(sku, {})
            store = STORE_INFO.get(store_id, {})
            
            inventory.append({
                'store_id': store_id,
                'store_name': store.get('name', store_id),
                'region': store.get('region', 'Unknown'),
                'sku': sku,
                'product_name': product.get('name', sku),
                'category': product.get('category', 'Unknown'),
                'current_stock': info['current_stock'],
                'forecasted_demand': info['forecasted_demand'],
                'order_qty': info['order_qty'],
                'risk_level': info['risk_level'],
                'days_of_stock': info['days_of_stock'],
                'order_value': info['order_value']
            })
    
    return pd.DataFrame(inventory)

@st.cache_data(ttl=60)
def get_summary_metrics():
    """Calculate summary metrics across all stores"""
    inventory_df = load_all_inventory()
    
    total_stores = len(SAMPLE_STORES)
    total_skus = len(PRODUCT_CATALOG)
    
    high_risk = len(inventory_df[inventory_df['risk_level'] == 'HIGH'])
    med_risk = len(inventory_df[inventory_df['risk_level'] == 'MED'])
    low_risk = len(inventory_df[inventory_df['risk_level'] == 'LOW'])
    
    total_order_value = inventory_df['order_value'].sum()
    items_to_reorder = len(inventory_df[inventory_df['order_qty'] > 0])
    
    return {
        'total_stores': total_stores,
        'total_skus': total_skus,
        'total_items': len(inventory_df),
        'high_risk': high_risk,
        'med_risk': med_risk,
        'low_risk': low_risk,
        'total_order_value': total_order_value,
        'items_to_reorder': items_to_reorder
    }

# ============================================================
# Visualization Functions
# ============================================================

def create_sales_history_chart(sales_df, forecast_df):
    """Create enhanced sales history and forecast visualization"""
    fig = go.Figure()
    
    # Historical sales
    fig.add_trace(go.Scatter(
        x=sales_df['date'],
        y=sales_df['units'],
        mode='lines',
        name='Historical Sales',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='Date: %{x}<br>Units: %{y}<extra></extra>'
    ))
    
    # 7-day moving average
    sales_df['ma7'] = sales_df['units'].rolling(window=7).mean()
    fig.add_trace(go.Scatter(
        x=sales_df['date'],
        y=sales_df['ma7'],
        mode='lines',
        name='7-Day Avg',
        line=dict(color='#2ecc71', width=2, dash='dot'),
        hovertemplate='Date: %{x}<br>7-Day Avg: %{y:.1f}<extra></extra>'
    ))
    
    # Forecast with confidence interval
    if len(forecast_df) > 0:
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=list(forecast_df['date']) + list(forecast_df['date'][::-1]),
            y=list(forecast_df['upper_bound']) + list(forecast_df['lower_bound'][::-1]),
            fill='toself',
            fillcolor='rgba(255, 127, 14, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Forecast Range',
            showlegend=True,
            hoverinfo='skip'
        ))
        
        # Forecast line
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['predicted_demand'],
            mode='lines+markers',
            name='14-Day Forecast',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            marker=dict(size=6),
            hovertemplate='Date: %{x}<br>Forecast: %{y:.1f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Sales History & Forecast (180 days + 14 day forecast)",
        xaxis_title="Date",
        yaxis_title="Units Sold",
        hovermode='x unified',
        height=400,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_category_breakdown_chart():
    """Create category breakdown pie chart"""
    inventory_df = load_all_inventory()
    category_data = inventory_df.groupby('category').agg({
        'current_stock': 'sum',
        'order_value': 'sum'
    }).reset_index()
    
    fig = px.pie(
        category_data, 
        values='current_stock', 
        names='category',
        title='Inventory by Category',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=350, showlegend=False)
    
    return fig

def create_risk_distribution_chart():
    """Create risk level distribution chart"""
    inventory_df = load_all_inventory()
    risk_data = inventory_df['risk_level'].value_counts().reset_index()
    risk_data.columns = ['Risk Level', 'Count']
    
    colors = {'HIGH': '#ff4444', 'MED': '#ffaa00', 'LOW': '#00cc44'}
    risk_data['Color'] = risk_data['Risk Level'].map(colors)
    
    fig = px.bar(
        risk_data,
        x='Risk Level',
        y='Count',
        color='Risk Level',
        color_discrete_map=colors,
        title='Risk Level Distribution'
    )
    fig.update_layout(height=350, showlegend=False)
    
    return fig

def create_regional_chart():
    """Create regional performance chart"""
    inventory_df = load_all_inventory()
    regional_data = inventory_df.groupby('region').agg({
        'order_value': 'sum',
        'order_qty': 'sum',
        'sku': 'count'
    }).reset_index()
    regional_data.columns = ['Region', 'Order Value', 'Order Qty', 'Items']
    
    fig = px.bar(
        regional_data,
        x='Region',
        y='Order Value',
        color='Order Qty',
        title='Order Value by Region',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=350)
    
    return fig

def get_risk_badge(risk_level):
    """Get HTML badge for risk level"""
    if risk_level == 'HIGH':
        return '🔴 <span class="risk-high">HIGH RISK</span>'
    elif risk_level == 'MED':
        return '🟡 <span class="risk-med">MEDIUM RISK</span>'
    else:
        return '🟢 <span class="risk-low">LOW RISK</span>'

def get_category_color(category):
    """Get color for category tag"""
    colors = {
        'Dairy': '#3498db',
        'Bakery': '#e67e22',
        'Eggs': '#f1c40f',
        'Meat': '#e74c3c',
        'Beverages': '#9b59b6',
        'Cereals': '#1abc9c',
        'Snacks': '#34495e',
        'Frozen': '#00bcd4'
    }
    return colors.get(category, '#95a5a6')

# ============================================================
# Main Dashboard
# ============================================================

def main():
    # Header
    st.markdown('<div class="main-header">📊 DemandIQ Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Retail Demand Forecasting & Replenishment Engine</div>', unsafe_allow_html=True)
    
    # Demo mode banner
    if DEMO_MODE:
        st.markdown('<div class="demo-banner">🎯 <strong>DEMO MODE</strong> - 10 Stores • 22 Products • 180-Day History</div>', unsafe_allow_html=True)
    
    # Summary metrics row
    metrics = get_summary_metrics()
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("🏪 Stores", metrics['total_stores'])
    with col2:
        st.metric("📦 Products", metrics['total_skus'])
    with col3:
        st.metric("🔴 High Risk", metrics['high_risk'])
    with col4:
        st.metric("🟡 Medium Risk", metrics['med_risk'])
    with col5:
        st.metric("📋 To Reorder", metrics['items_to_reorder'])
    with col6:
        st.metric("💰 Order Value", f"${metrics['total_order_value']:,.0f}")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 SKU Analysis", "🏪 Store Overview", "📈 Analytics", "📋 Full Inventory"])
    
    # ============================================================
    # TAB 1: SKU Analysis
    # ============================================================
    with tab1:
        # Sidebar filters
        with st.sidebar:
            st.header("🔍 Filters")
            
            # Store selection
            stores = load_stores()
            store_options = [f"{s} - {STORE_INFO[s]['name']}" for s in stores]
            selected_store_option = st.selectbox("Select Store", store_options)
            selected_store = selected_store_option.split(" - ")[0]
            
            # Show store info
            store_info = load_store_info(selected_store)
            st.caption(f"📍 Region: {store_info.get('region', 'N/A')}")
            st.caption(f"🏬 Type: {store_info.get('type', 'N/A')}")
            st.caption(f"📏 Size: {store_info.get('size', 'N/A')}")
            
            st.markdown("---")
            
            # SKU selection with category filter
            skus = load_skus(selected_store)
            sku_options = [f"{s} - {PRODUCT_CATALOG.get(s, {}).get('name', s)}" for s in skus]
            selected_sku_option = st.selectbox("Select Product", sku_options)
            selected_sku = selected_sku_option.split(" - ")[0]
            
            # Show product info
            product_info = load_product_info(selected_sku)
            if product_info:
                cat_color = get_category_color(product_info.get('category', ''))
                st.markdown(f"<span style='background-color: {cat_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;'>{product_info.get('category', 'N/A')}</span>", unsafe_allow_html=True)
                st.caption(f"💵 Price: ${product_info.get('unit_price', 0):.2f}")
                st.caption(f"🚚 Lead Time: {product_info.get('lead_time', 'N/A')} days")
                st.caption(f"🏭 Supplier: {product_info.get('supplier', 'N/A')}")
            
            st.markdown("---")
            
            # Risk filter for alerts
            st.subheader("⚠️ Alert Filters")
            risk_filter = st.multiselect(
                "Risk Level",
                ["HIGH", "MED", "LOW"],
                default=["HIGH", "MED"]
            )
        
        # Main content
        if selected_store and selected_sku:
            # Load data
            sales_df = load_sales_history(selected_store, selected_sku, days=180)
            forecast_df = load_forecast(selected_store, selected_sku, days=14)
            reorder_info = load_reorder_info(selected_store, selected_sku)
            
            # Key metrics row
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.metric("📦 Current Stock", f"{int(reorder_info['current_stock']):,}")
            with col2:
                st.metric("📈 7-Day Forecast", f"{reorder_info['forecasted_demand']:.0f}")
            with col3:
                st.metric("🛡️ Safety Stock", f"{reorder_info['safety_stock']:.0f}")
            with col4:
                delta_color = "inverse" if reorder_info['days_of_stock'] < 3 else "normal"
                st.metric("📅 Days of Stock", f"{reorder_info['days_of_stock']:.1f}")
            with col5:
                st.metric("🛒 Order Qty", f"{int(reorder_info['order_qty']):,}")
            with col6:
                st.metric("💰 Order Value", f"${reorder_info['order_value']:,.2f}")
            
            st.markdown("---")
            
            # Sales chart and reorder panel
            col1, col2 = st.columns([2, 1])
            
            with col1:
                chart = create_sales_history_chart(sales_df, forecast_df)
                st.plotly_chart(chart, use_container_width=True)
            
            with col2:
                st.subheader("📋 Reorder Recommendation")
                
                # Risk badge
                st.markdown(get_risk_badge(reorder_info['risk_level']), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Details
                st.markdown(f"**🚚 Supplier:** {reorder_info['supplier']}")
                st.markdown(f"**⏱️ Lead Time:** {reorder_info['lead_time']} days")
                st.markdown(f"**📊 Profit Margin:** {reorder_info['profit_margin']}%")
                st.markdown(f"**💵 Potential Revenue:** ${reorder_info['potential_revenue']:,.2f}")
                
                st.markdown("---")
                
                # Action buttons
                if reorder_info['order_qty'] > 0:
                    if st.button(f"📦 Order {int(reorder_info['order_qty']):,} Units", type="primary", key="order_btn"):
                        result = send_reorder_notification(
                            store_id=selected_store,
                            sku=selected_sku,
                            order_qty=int(reorder_info['order_qty']),
                            current_stock=int(reorder_info['current_stock']),
                            forecasted_demand=reorder_info['forecasted_demand'],
                            risk_level=reorder_info['risk_level'],
                            safety_stock=reorder_info['safety_stock']
                        )
                        
                        if result['success']:
                            st.success("✅ Reorder placed! Telegram notification sent.")
                        else:
                            st.warning(f"⚠️ Reorder placed, but notification failed: {result['error']}")
                else:
                    st.success("✅ Stock levels adequate")
                
                # Download forecast
                csv = forecast_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Forecast",
                    data=csv,
                    file_name=f"forecast_{selected_store}_{selected_sku}.csv",
                    mime="text/csv"
                )
            
            st.markdown("---")
            
            # At-risk products for this store
            st.subheader(f"⚠️ At-Risk Products - {STORE_INFO[selected_store]['name']}")
            
            inventory_df = load_all_inventory()
            alerts_df = inventory_df[(inventory_df['store_id'] == selected_store) & 
                                     (inventory_df['risk_level'].isin(risk_filter))]
            
            if len(alerts_df) > 0:
                display_df = alerts_df[['product_name', 'category', 'current_stock', 'forecasted_demand', 
                                        'days_of_stock', 'order_qty', 'order_value', 'risk_level']].copy()
                display_df.columns = ['Product', 'Category', 'Stock', 'Forecast', 'Days Left', 'Order Qty', 'Order Value', 'Risk']
                
                def highlight_risk(row):
                    if row['Risk'] == 'HIGH':
                        return ['background-color: #ffcccc'] * len(row)
                    elif row['Risk'] == 'MED':
                        return ['background-color: #fff4cc'] * len(row)
                    return [''] * len(row)
                
                styled_df = display_df.style.apply(highlight_risk, axis=1).format({
                    'Order Value': '${:,.2f}',
                    'Days Left': '{:.1f}'
                })
                st.dataframe(styled_df, use_container_width=True, height=300)
            else:
                st.success("✅ No products at risk in selected filters!")
    
    # ============================================================
    # TAB 2: Store Overview
    # ============================================================
    with tab2:
        st.subheader("🏪 Store Performance Overview")
        
        inventory_df = load_all_inventory()
        
        # Store summary table
        store_summary = inventory_df.groupby(['store_id', 'store_name', 'region']).agg({
            'sku': 'count',
            'current_stock': 'sum',
            'order_qty': 'sum',
            'order_value': 'sum',
            'risk_level': lambda x: (x == 'HIGH').sum()
        }).reset_index()
        store_summary.columns = ['Store ID', 'Store Name', 'Region', 'SKUs', 'Total Stock', 'Total Order Qty', 'Order Value', 'High Risk Items']
        
        st.dataframe(
            store_summary.style.format({
                'Order Value': '${:,.2f}',
                'Total Stock': '{:,.0f}',
                'Total Order Qty': '{:,.0f}'
            }),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = store_summary.to_csv(index=False)
        st.download_button(
            label="📥 Download Store Summary",
            data=csv,
            file_name="store_summary.csv",
            mime="text/csv"
        )
    
    # ============================================================
    # TAB 3: Analytics
    # ============================================================
    with tab3:
        st.subheader("📈 Inventory Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_category_breakdown_chart()
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = create_risk_distribution_chart()
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_regional_chart()
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top products needing reorder
            inventory_df = load_all_inventory()
            top_reorder = inventory_df.nlargest(10, 'order_value')[['product_name', 'store_name', 'order_qty', 'order_value', 'risk_level']]
            top_reorder.columns = ['Product', 'Store', 'Order Qty', 'Order Value', 'Risk']
            
            st.markdown("**🔝 Top 10 Products by Order Value**")
            st.dataframe(
                top_reorder.style.format({'Order Value': '${:,.2f}'}),
                use_container_width=True,
                height=350
            )
    
    # ============================================================
    # TAB 4: Full Inventory
    # ============================================================
    with tab4:
        st.subheader("📋 Complete Inventory Status")
        
        inventory_df = load_all_inventory()
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            region_filter = st.multiselect("Filter by Region", inventory_df['region'].unique().tolist(), default=inventory_df['region'].unique().tolist())
        with col2:
            category_filter = st.multiselect("Filter by Category", inventory_df['category'].unique().tolist(), default=inventory_df['category'].unique().tolist())
        with col3:
            risk_filter_full = st.multiselect("Filter by Risk", ['HIGH', 'MED', 'LOW'], default=['HIGH', 'MED', 'LOW'])
        
        # Apply filters
        filtered_df = inventory_df[
            (inventory_df['region'].isin(region_filter)) &
            (inventory_df['category'].isin(category_filter)) &
            (inventory_df['risk_level'].isin(risk_filter_full))
        ]
        
        # Display
        display_cols = ['store_name', 'region', 'product_name', 'category', 'current_stock', 
                        'forecasted_demand', 'days_of_stock', 'order_qty', 'order_value', 'risk_level']
        
        st.dataframe(
            filtered_df[display_cols].rename(columns={
                'store_name': 'Store',
                'region': 'Region',
                'product_name': 'Product',
                'category': 'Category',
                'current_stock': 'Stock',
                'forecasted_demand': 'Forecast',
                'days_of_stock': 'Days Left',
                'order_qty': 'Order Qty',
                'order_value': 'Order Value',
                'risk_level': 'Risk'
            }).style.format({
                'Order Value': '${:,.2f}',
                'Days Left': '{:.1f}'
            }),
            use_container_width=True,
            height=500
        )
        
        # Download full inventory
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Inventory",
            data=csv,
            file_name="full_inventory.csv",
            mime="text/csv"
        )
    
    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | DemandIQ v2.0")

if __name__ == "__main__":
    main()
