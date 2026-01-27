"""
Prophet Model Training
Time series forecasting with seasonality and holidays
"""
import pandas as pd
import numpy as np
from pathlib import Path
from prophet import Prophet
import pickle
import sys
sys.path.append(str(Path(__file__).parent.parent))
from db.db_utils import get_engine
import mlflow
import mlflow.sklearn

def load_training_data(store_id=None, sku=None, limit_skus=None):
    """Load data for model training"""
    engine = get_engine()
    
    query = "SELECT date, store_id, sku, units FROM sales ORDER BY date"
    
    if store_id and sku:
        query = f"""
        SELECT date, store_id, sku, units 
        FROM sales 
        WHERE store_id = '{store_id}' AND sku = '{sku}'
        ORDER BY date
        """
    elif limit_skus:
        # Get top N SKUs by total volume for faster training
        query = f"""
        WITH top_skus AS (
            SELECT store_id, sku
            FROM sales
            GROUP BY store_id, sku
            ORDER BY SUM(units) DESC
            LIMIT {limit_skus}
        )
        SELECT s.date, s.store_id, s.sku, s.units
        FROM sales s
        INNER JOIN top_skus t ON s.store_id = t.store_id AND s.sku = t.sku
        ORDER BY s.date
        """
    
    df = pd.read_sql(query, engine)
    df['date'] = pd.to_datetime(df['date'])
    
    return df

def train_prophet_model(df, store_id, sku):
    """Train Prophet model for a single SKU"""
    # Prepare data in Prophet format
    prophet_df = df[df['store_id'] == store_id][df['sku'] == sku][['date', 'units']].copy()
    prophet_df.columns = ['ds', 'y']
    
    if len(prophet_df) < 30:  # Skip if insufficient data
        return None, None
    
    # Initialize Prophet with seasonality
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10
    )
    
    # Add US holidays
    model.add_country_holidays(country_name='US')
    
    # Train model
    model.fit(prophet_df)
    
    # Make 7-day forecast
    future = model.make_future_dataframe(periods=7)
    forecast = model.predict(future)
    
    # Get forecast for next 7 days
    forecast_7d = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7)
    
    # Calculate MAE on training data
    train_pred = forecast[forecast['ds'].isin(prophet_df['ds'])]['yhat'].values
    train_actual = prophet_df['y'].values
    mae = np.mean(np.abs(train_pred - train_actual))
    
    return model, {'mae': mae, 'forecast': forecast_7d}

def train_all_models(limit_skus=10):
    """Train Prophet models for multiple SKUs"""
    print("=" * 60)
    print("DemandIQ - Prophet Model Training")
    print("=" * 60)
    
    # Set up MLflow
    mlflow.set_experiment("demandiq_prophet")
    
    # Load data
    print(f"\nLoading data for top {limit_skus} SKUs...")
    df = load_training_data(limit_skus=limit_skus)
    
    # Get unique store-SKU combinations
    store_sku_combos = df.groupby(['store_id', 'sku']).size().reset_index()[['store_id', 'sku']]
    print(f"Training models for {len(store_sku_combos)} store-SKU combinations...")
    
    # Create models directory
    models_dir = Path('models/saved/prophet')
    models_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for idx, row in store_sku_combos.iterrows():
        store_id = row['store_id']
        sku = row['sku']
        
        print(f"\n[{idx+1}/{len(store_sku_combos)}] Training: {store_id} - {sku}")
        
        with mlflow.start_run(run_name=f"{store_id}_{sku}"):
            model, metrics = train_prophet_model(df, store_id, sku)
            
            if model is None:
                print(f"  ✗ Skipped (insufficient data)")
                continue
            
            # Log metrics
            mlflow.log_param("store_id", store_id)
            mlflow.log_param("sku", sku)
            mlflow.log_param("model_type", "prophet")
            mlflow.log_metric("mae", metrics['mae'])
            
            # Save model
            model_path = models_dir / f"{store_id}_{sku}_prophet.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            mlflow.log_artifact(str(model_path))
            
            print(f"  ✓ MAE: {metrics['mae']:.2f}")
            
            results.append({
                'store_id': store_id,
                'sku': sku,
                'model_type': 'prophet',
                'mae': metrics['mae'],
                'model_path': str(model_path)
            })
    
    # Save results summary
    results_df = pd.DataFrame(results)
    results_path = Path('models/saved/prophet_results.csv')
    results_df.to_csv(results_path, index=False)
    
    print("\n" + "=" * 60)
    print(f"✓ Prophet training complete!")
    print(f"  Trained {len(results)} models")
    print(f"  Average MAE: {results_df['mae'].mean():.2f}")
    print(f"  Results saved to: {results_path}")
    print("=" * 60)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--subset', type=int, default=10, help='Number of SKUs to train on')
    args = parser.parse_args()
    
    train_all_models(limit_skus=args.subset)
