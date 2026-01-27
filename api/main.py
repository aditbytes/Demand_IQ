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
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from db.db_utils import get_engine

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
    engine = get_engine()
    
    query = f"""
    SELECT forecast_date, predicted_demand
    FROM forecast
    WHERE store_id = '{store_id}' 
    AND sku = '{sku}'
    AND forecast_date >= CURRENT_DATE
    AND forecast_date < CURRENT_DATE + INTERVAL '{days} days'
    ORDER BY forecast_date
    """
    
    df = pd.read_sql(query, engine)
    
    if len(df) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No forecast found for store_id={store_id}, sku={sku}"
        )
    
    forecasts = [
        ForecastItem(
            date=row['forecast_date'].strftime('%Y-%m-%d'),
            predicted_demand=float(row['predicted_demand'])
        )
        for _, row in df.iterrows()
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
    engine = get_engine()
    
    query = f"""
    SELECT current_stock, forecasted_demand, safety_stock, order_qty, risk_level
    FROM reorders
    WHERE store_id = '{store_id}' AND sku = '{sku}'
    """
    
    df = pd.read_sql(query, engine)
    
    if len(df) == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No reorder data found for store_id={store_id}, sku={sku}"
        )
    
    row = df.iloc[0]
    
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
    engine = get_engine()
    
    query = """
    SELECT store_id, sku, current_stock, forecasted_demand, order_qty, risk_level
    FROM reorders
    WHERE 1=1
    """
    
    if risk_level:
        query += f" AND risk_level = '{risk_level}'"
    else:
        # Default: show MED and HIGH risk items
        query += " AND risk_level IN ('MED', 'HIGH')"
    
    query += f" ORDER BY CASE risk_level WHEN 'HIGH' THEN 1 WHEN 'MED' THEN 2 ELSE 3 END, order_qty DESC LIMIT {limit}"
    
    df = pd.read_sql(query, engine)
    
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
    from db.db_utils import test_connection
    
    db_status = test_connection()
    
    return {
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
