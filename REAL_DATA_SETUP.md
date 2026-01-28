# DemandIQ Dashboard - Real Data Setup Guide (CSV)

This guide explains how to use **real data from CSV files** instead of demo mode.

---

## File Structure

Create CSV files in the `data/` directory:

```
Demand_IQ/
├── data/
│   ├── sales.csv
│   ├── forecast.csv
│   └── reorders.csv
└── dashboard/
    └── app.py
```

---

## Step 1: Prepare Your CSV Files

### sales.csv
```csv
store_id,sku,date,units,price,promo
STORE-001,SKU-MILK-001,2026-01-01,45,4.99,False
STORE-001,SKU-MILK-001,2026-01-02,52,4.99,False
STORE-001,SKU-BREAD-002,2026-01-01,38,3.49,True
...
```

**Required columns:** `store_id`, `sku`, `date`, `units`, `price`, `promo`

---

### forecast.csv
```csv
store_id,sku,forecast_date,predicted_demand
STORE-001,SKU-MILK-001,2026-01-29,48.5
STORE-001,SKU-MILK-001,2026-01-30,52.3
STORE-001,SKU-MILK-001,2026-01-31,45.1
...
```

**Required columns:** `store_id`, `sku`, `forecast_date`, `predicted_demand`

---

### reorders.csv
```csv
store_id,sku,current_stock,forecasted_demand,safety_stock,order_qty,risk_level
STORE-001,SKU-MILK-001,90,169,33,112,HIGH
STORE-001,SKU-BREAD-002,150,120,24,0,LOW
STORE-002,SKU-EGGS-003,45,180,36,171,HIGH
...
```

**Required columns:** `store_id`, `sku`, `current_stock`, `forecasted_demand`, `safety_stock`, `order_qty`, `risk_level`

**risk_level values:** `LOW`, `MED`, `HIGH`

---

## Step 2: Update app.py

Replace the data loading section in `dashboard/app.py`:

### Change DEMO_MODE
```python
DEMO_MODE = False  # Set to False for real CSV data
USE_CSV = True     # Add this line
```

### Add CSV path configuration (after DEMO_MODE)
```python
import os

# CSV file paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
SALES_CSV = os.path.join(DATA_DIR, 'sales.csv')
FORECAST_CSV = os.path.join(DATA_DIR, 'forecast.csv')
REORDERS_CSV = os.path.join(DATA_DIR, 'reorders.csv')
```

### Replace data loading functions
```python
@st.cache_data(ttl=300)
def load_stores():
    df = pd.read_csv(SALES_CSV)
    return sorted(df['store_id'].unique().tolist())

@st.cache_data(ttl=300)
def load_skus(store_id=None):
    df = pd.read_csv(SALES_CSV)
    if store_id:
        df = df[df['store_id'] == store_id]
    return sorted(df['sku'].unique().tolist())

@st.cache_data(ttl=60)
def load_sales_history(store_id, sku, days=90):
    df = pd.read_csv(SALES_CSV)
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['store_id'] == store_id) & (df['sku'] == sku)]
    cutoff = datetime.now() - timedelta(days=days)
    df = df[df['date'] >= cutoff].sort_values('date')
    return df

@st.cache_data(ttl=60)
def load_forecast(store_id, sku):
    df = pd.read_csv(FORECAST_CSV)
    df['date'] = pd.to_datetime(df['forecast_date'])
    df = df[(df['store_id'] == store_id) & (df['sku'] == sku)]
    df = df[df['date'] >= datetime.now()].head(7)
    return df[['date', 'predicted_demand']]

@st.cache_data(ttl=60)
def load_reorder_info(store_id, sku):
    df = pd.read_csv(REORDERS_CSV)
    df = df[(df['store_id'] == store_id) & (df['sku'] == sku)]
    return df.iloc[0] if len(df) > 0 else None

@st.cache_data(ttl=60)
def load_alerts(store_id=None, risk_level=None):
    df = pd.read_csv(REORDERS_CSV)
    if store_id:
        df = df[df['store_id'] == store_id]
    if risk_level:
        df = df[df['risk_level'] == risk_level]
    else:
        df = df[df['risk_level'].isin(['MED', 'HIGH'])]
    # Sort by risk priority
    risk_order = {'HIGH': 0, 'MED': 1, 'LOW': 2}
    df['_order'] = df['risk_level'].map(risk_order)
    df = df.sort_values(['_order', 'order_qty'], ascending=[True, False])
    return df.drop('_order', axis=1)
```

---

## Step 3: Run the Dashboard

```bash
cd "/Volumes/Aditya ssd/Demand_IQ/dashboard"
streamlit run app.py
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `FileNotFoundError` | Check CSV files exist in `data/` folder |
| `KeyError: 'column_name'` | Verify CSV has all required columns |
| No data showing | Check store_id/sku values match across files |
| Date parsing errors | Use format `YYYY-MM-DD` in CSV |

---

## Updating Data

Simply replace or update the CSV files. Click **Rerun** in Streamlit or restart the app to load new data.

For automated updates, your ML pipeline can write directly to these CSV files.
