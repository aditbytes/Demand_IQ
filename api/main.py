"""
DemandIQ FastAPI Application
Production-grade API for demand forecasting and reorder recommendations
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from datetime import date, datetime
from pathlib import Path


# Data file paths
DATA_DIR = Path(__file__).parent.parent / 'data'
SALES_CSV = DATA_DIR / 'processed' / 'sales_cleaned.csv'
FORECAST_CSV = DATA_DIR / 'forecast.csv'
REORDERS_CSV = DATA_DIR / 'reorders.csv'

# Initialize FastAPI app
app = FastAPI(
    title="DemandIQ API",
    description="Retail Demand Forecasting & Replenishment Engine",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ForecastItem(BaseModel):
    date: str
    predicted_demand: float

class ForecastResponse(BaseModel):
    store_id: str
    sku: str
    forecast_period_days: int
    forecasts: List[ForecastItem]

class ReorderResponse(BaseModel):
    store_id: str
    sku: str
    current_stock: int
    forecasted_demand: float
    safety_stock: float
    reorder_qty: int
    risk_level: str

class AlertItem(BaseModel):
    store_id: str
    sku: str
    current_stock: int
    forecasted_demand: float
    reorder_qty: int
    risk_level: str

# Data loading functions
def load_forecast_data():
    """Load forecast data from CSV"""
    if FORECAST_CSV.exists():
        df = pd.read_csv(FORECAST_CSV)
        df['forecast_date'] = pd.to_datetime(df['forecast_date'])
        return df
    return pd.DataFrame()

def load_reorders_data():
    """Load reorder recommendations from CSV"""
    if REORDERS_CSV.exists():
        return pd.read_csv(REORDERS_CSV)
    return pd.DataFrame()

def load_sales_data():
    """Load sales data from CSV"""
    if SALES_CSV.exists():
        df = pd.read_csv(SALES_CSV)
        df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame()

# Endpoints
@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "DemandIQ API",
        "version": "1.0.0",
        "endpoints": {
            "forecast": "/forecast/{store_id}/{sku}",
            "reorder": "/reorder/{store_id}/{sku}",
            "alerts": "/alerts"
        }
    }

@app.get("/forecast/{store_id}/{sku}", response_model=ForecastResponse)
def get_forecast(store_id: str, sku: str, days: int = 7):
    """
    Get demand forecast for a specific store-SKU combination
    
    Args:
        store_id: Store identifier
        sku: Product SKU
        days: Number of days to forecast (default: 7)
    
    Returns:
        Forecast for next N days
    """
    df = load_forecast_data()
    
    if len(df) == 0:
        raise HTTPException(
            status_code=404,
            detail="Forecast data not available. Run the forecasting pipeline first."
        )
    
    # Filter for store and SKU
    df_filtered = df[(df['store_id'] == store_id) & (df['sku'] == sku)]
    
    # Filter for future dates
    today = pd.Timestamp.now().normalize()
    df_filtered = df_filtered[df_filtered['forecast_date'] >= today].head(days)
    
    if len(df_filtered) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No forecast found for store_id={store_id}, sku={sku}"
        )
    
    forecasts = [
        ForecastItem(
            date=row['forecast_date'].strftime('%Y-%m-%d'),
            predicted_demand=float(row['predicted_demand'])
        )
        for _, row in df_filtered.iterrows()
    ]
    
    return ForecastResponse(
        store_id=store_id,
        sku=sku,
        forecast_period_days=days,
        forecasts=forecasts
    )

@app.get("/reorder/{store_id}/{sku}", response_model=ReorderResponse)
def get_reorder(store_id: str, sku: str):
    """
    Get reorder recommendation for a specific store-SKU combination
    
    Args:
        store_id: Store identifier
        sku: Product SKU
    
    Returns:
        Reorder quantity and risk level
    """
    df = load_reorders_data()
    
    if len(df) == 0:
        raise HTTPException(
            status_code=404,
            detail="Reorder data not available. Run the reorder pipeline first."
        )
    
    # Filter for store and SKU
    df_filtered = df[(df['store_id'] == store_id) & (df['sku'] == sku)]
    
    if len(df_filtered) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No reorder data found for store_id={store_id}, sku={sku}"
        )
    
    row = df_filtered.iloc[0]
    
    return ReorderResponse(
        store_id=store_id,
        sku=sku,
        current_stock=int(row['current_stock']) if pd.notna(row['current_stock']) else 0,
        forecasted_demand=float(row['forecasted_demand']),
        safety_stock=float(row['safety_stock']),
        reorder_qty=int(row['order_qty']),
        risk_level=row['risk_level']
    )

@app.get("/alerts", response_model=List[AlertItem])
def get_alerts(
    risk_level: Optional[str] = Query(None, regex="^(LOW|MED|HIGH)$"),
    limit: int = Query(50, ge=1, le=500)
):
    """
    Get alerts for products at risk of stockout
    
    Args:
        risk_level: Filter by risk level (LOW, MED, HIGH). Optional.
        limit: Maximum number of results (default: 50, max: 500)
    
    Returns:
        List of products at risk
    """
    df = load_reorders_data()
    
    if len(df) == 0:
        return []
    
    # Filter by risk level
    if risk_level:
        df = df[df['risk_level'] == risk_level]
    else:
        # Default: show MED and HIGH risk items
        df = df[df['risk_level'].isin(['MED', 'HIGH'])]
    
    # Sort by risk priority
    risk_order = {'HIGH': 0, 'MED': 1, 'LOW': 2}
    df['_order'] = df['risk_level'].map(risk_order)
    df = df.sort_values(['_order', 'order_qty'], ascending=[True, False])
    df = df.drop('_order', axis=1)
    
    # Limit results
    df = df.head(limit)
    
    alerts = [
        AlertItem(
            store_id=row['store_id'],
            sku=row['sku'],
            current_stock=int(row['current_stock']) if pd.notna(row['current_stock']) else 0,
            forecasted_demand=float(row['forecasted_demand']),
            reorder_qty=int(row['order_qty']),
            risk_level=row['risk_level']
        )
        for _, row in df.iterrows()
    ]
    
    return alerts

@app.get("/health")
def health_check():
    """Health check endpoint"""
    # Check if data files exist
    sales_ok = SALES_CSV.exists()
    forecast_ok = FORECAST_CSV.exists()
    reorders_ok = REORDERS_CSV.exists()
    
    status = "healthy" if (sales_ok or reorders_ok) else "degraded"
    
    return {
        "status": status,
        "data_files": {
            "sales": "available" if sales_ok else "missing",
            "forecast": "available" if forecast_ok else "missing",
            "reorders": "available" if reorders_ok else "missing"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
