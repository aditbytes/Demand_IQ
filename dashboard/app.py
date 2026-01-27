"""
DemandIQ Streamlit Dashboard
Store manager interface for demand forecasting and reorder recommendations
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from db.db_utils import get_engine

# Page configuration
st.set_page_config(
    page_title="DemandIQ Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
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
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_db_engine():
    return get_engine()

# Data loading functions
@st.cache_data(ttl=300)
def load_stores():
    """Load available stores"""
    engine = get_db_engine()
    df = pd.read_sql("SELECT DISTINCT store_id FROM sales ORDER BY store_id", engine)
    return df['store_id'].tolist()

@st.cache_data(ttl=300)
def load_skus(store_id=None):
    """Load available SKUs"""
    engine = get_db_engine()
    query = "SELECT DISTINCT sku FROM sales"
    if store_id:
        query += f" WHERE store_id = '{store_id}'"
    query += " ORDER BY sku"
    df = pd.read_sql(query, engine)
    return df['sku'].tolist()

@st.cache_data(ttl=60)
def load_sales_history(store_id, sku, days=90):
    """Load sales history"""
    engine = get_db_engine()
    query = f"""
    SELECT date, units, price, promo
    FROM sales
    WHERE store_id = '{store_id}' AND sku = '{sku}'
    AND date >= CURRENT_DATE - INTERVAL '{days} days'
    ORDER BY date
    """
    df = pd.read_sql(query, engine)
    df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_data(ttl=60)
def load_forecast(store_id, sku):
    """Load forecast data"""
    engine = get_db_engine()
    query = f"""
    SELECT forecast_date as date, predicted_demand
    FROM forecast
    WHERE store_id = '{store_id}' AND sku = '{sku}'
    AND forecast_date >= CURRENT_DATE
    ORDER BY forecast_date
    LIMIT 7
    """
    df = pd.read_sql(query, engine)
    if len(df) > 0:
        df['date'] = pd.to_datetime(df['date'])
    return df

@st.cache_data(ttl=60)
def load_reorder_info(store_id, sku):
    """Load reorder recommendation"""
    engine = get_db_engine()
    query = f"""
    SELECT current_stock, forecasted_demand, safety_stock, order_qty, risk_level
    FROM reorders
    WHERE store_id = '{store_id}' AND sku = '{sku}'
    """
    df = pd.read_sql(query, engine)
    return df.iloc[0] if len(df) > 0 else None

@st.cache_data(ttl=60)
def load_alerts(store_id=None, risk_level=None):
    """Load at-risk products"""
    engine = get_db_engine()
    query = "SELECT * FROM reorders WHERE 1=1"
    
    if store_id:
        query += f" AND store_id = '{store_id}'"
    
    if risk_level:
        query += f" AND risk_level = '{risk_level}'"
    else:
        query += " AND risk_level IN ('MED', 'HIGH')"
    
    query += " ORDER BY CASE risk_level WHEN 'HIGH' THEN 1 WHEN 'MED' THEN 2 ELSE 3 END, order_qty DESC LIMIT 50"
    
    df = pd.read_sql(query, engine)
    return df

# Visualization functions
def create_sales_history_chart(sales_df, forecast_df):
    """Create sales history and forecast visualization"""
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
    
    # Forecast
    if len(forecast_df) > 0:
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['predicted_demand'],
            mode='lines+markers',
            name='7-Day Forecast',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            marker=dict(size=8),
            hovertemplate='Date: %{x}<br>Forecast: %{y:.1f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Sales History & Forecast",
        xaxis_title="Date",
        yaxis_title="Units Sold",
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    return fig

def get_risk_badge(risk_level):
    """Get HTML badge for risk level"""
    if risk_level == 'HIGH':
        return '🔴 <span class="risk-high">HIGH RISK</span>'
    elif risk_level == 'MED':
        return '🟡 <span class="risk-med">MEDIUM RISK</span>'
    else:
        return '🟢 <span class="risk-low">LOW RISK</span>'

# Main dashboard
def main():
    # Header
    st.markdown('<div class="main-header">📊 DemandIQ Dashboard</div>', unsafe_allow_html=True)
    st.markdown("**Retail Demand Forecasting & Replenishment Engine**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("Filters")
        
        # Store selection
        stores = load_stores()
        if len(stores) == 0:
            st.error("No store data available. Please run data pipelines first.")
            return
        
        selected_store = st.selectbox("Select Store", stores)
        
        # SKU selection
        skus = load_skus(selected_store)
        if len(skus) == 0:
            st.error("No SKU data available for this store.")
            return
        
        selected_sku = st.selectbox("Select SKU", skus)
        
        st.markdown("---")
        
        # Risk filter for alerts
        st.subheader("Alert Filters")
        risk_filter = st.multiselect(
            "Risk Level",
            ["HIGH", "MED", "LOW"],
            default=["HIGH", "MED"]
        )
    
    # Main content
    if selected_store and selected_sku:
        # Load data
        sales_df = load_sales_history(selected_store, selected_sku)
        forecast_df = load_forecast(selected_store, selected_sku)
        reorder_info = load_reorder_info(selected_store, selected_sku)
        
        # Row 1: Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        if reorder_info is not None:
            with col1:
                st.metric("Current Stock", f"{int(reorder_info['current_stock']):,} units")
            
            with col2:
                st.metric("7-Day Forecast", f"{reorder_info['forecasted_demand']:.0f} units")
            
            with col3:
                st.metric("Safety Stock", f"{reorder_info['safety_stock']:.0f} units")
            
            with col4:
                st.metric("Reorder Qty", f"{int(reorder_info['order_qty']):,} units")
        
        st.markdown("---")
        
        # Row 2: Sales chart and reorder recommendation
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if len(sales_df) > 0:
                chart = create_sales_history_chart(sales_df, forecast_df)
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("No sales history available for this SKU")
        
        with col2:
            st.subheader("Reorder Recommendation")
            
            if reorder_info is not None:
                # Risk badge
                st.markdown(get_risk_badge(reorder_info['risk_level']), unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Recommendation details
                st.markdown(f"**Current Stock:** {int(reorder_info['current_stock']):,} units")
                st.markdown(f"**Forecasted Demand:** {reorder_info['forecasted_demand']:.0f} units")
                st.markdown(f"**Safety Stock:** {reorder_info['safety_stock']:.0f} units")
                st.markdown(f"**Recommended Order:** {int(reorder_info['order_qty']):,} units")
                
                # Action button
                if reorder_info['order_qty'] > 0:
                    st.button(f"📦 Order {int(reorder_info['order_qty']):,} Units", type="primary", use_container_width=True)
                else:
                    st.success("✅ Stock levels adequate")
            else:
                st.warning("No reorder data available for this SKU")
        
        st.markdown("---")
        
        # Row 3: At-risk products table
        st.subheader(f"⚠️ At-Risk Products - {selected_store}")
        
        alerts_df = load_alerts(selected_store, risk_filter[0] if len(risk_filter) == 1 else None)
        
        if len(alerts_df) > 0:
            # Format the dataframe
            display_df = alerts_df[['sku', 'current_stock', 'forecasted_demand', 'order_qty', 'risk_level']].copy()
            display_df.columns = ['SKU', 'Current Stock', 'Forecast', 'Order Qty', 'Risk']
            
            # Color code by risk
            def highlight_risk(row):
                if row['Risk'] == 'HIGH':
                    return ['background-color: #ffcccc'] * len(row)
                elif row['Risk'] == 'MED':
                    return ['background-color: #fff4cc'] * len(row)
                else:
                    return [''] * len(row)
            
            styled_df = display_df.style.apply(highlight_risk, axis=1)
            st.dataframe(styled_df, use_container_width=True, height=300)
        else:
            st.success("✅ No products at risk!")
    
    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
