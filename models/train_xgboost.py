"""
XGBoost Model Training
Gradient boosting with engineered features
"""
import pandas as pd
import numpy as np
from pathlib import Path
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle
import sys
sys.path.append(str(Path(__file__).parent.parent))
from db.db_utils import get_engine
import mlflow
import mlflow.xgboost

def load_features(limit_skus=None):
    """Load engineered features from database"""
    engine = get_engine()
    
    if limit_skus:
        query = f"""
        WITH top_skus AS (
            SELECT store_id, sku
            FROM sales
            GROUP BY store_id, sku
            ORDER BY SUM(units) DESC
            LIMIT {limit_skus}
        )
        SELECT f.*
        FROM features f
        INNER JOIN top_skus t ON f.store_id = t.store_id AND f.sku = t.sku
        ORDER BY f.date
        """
    else:
        query = "SELECT * FROM features ORDER BY date"
    
    df = pd.read_sql(query, engine)
    df['date'] = pd.to_datetime(df['date'])
    
    return df

def prepare_training_data(df, store_id, sku):
    """Prepare features and target for a single SKU"""
    # Filter for specific store-SKU
    df_sku = df[(df['store_id'] == store_id) & (df['sku'] == sku)].copy()
    
    if len(df_sku) < 50:  # Skip if insufficient data
        return None, None, None, None
    
    # Feature columns
    feature_cols = [
        'lag7', 'lag14', 'lag28',
        'rolling7_mean', 'rolling7_std',
        'rolling30_mean', 'rolling30_std',
        'price', 'price_change',
        'day_of_week', 'month', 'is_holiday', 'is_snap'
    ]
    
    # Convert boolean to int
    df_sku['promo'] = df_sku['promo'].astype(int)
    df_sku['is_holiday'] = df_sku['is_holiday'].astype(int)
    df_sku['is_snap'] = df_sku['is_snap'].astype(int)
    
    feature_cols.append('promo')
    
    X = df_sku[feature_cols].fillna(0)
    
    # Target: next day's units (shift by -1)
    y = df_sku['units'].shift(-1).fillna(0)
    
    # Remove last row (no target)
    X = X[:-1]
    y = y[:-1]
    
    # Train-test split (80-20)
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    return X_train, X_test, y_train, y_test

def train_xgboost_model(X_train, X_test, y_train, y_test):
    """Train XGBoost model"""
    params = {
        'objective': 'reg:squarederror',
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 100,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42
    }
    
    model = xgb.XGBRegressor(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        early_stopping_rounds=10,
        verbose=False
    )
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    return model, {'mae': mae, 'rmse': rmse}

def train_all_models(limit_skus=10):
    """Train XGBoost models for multiple SKUs"""
    print("=" * 60)
    print("DemandIQ - XGBoost Model Training")
    print("=" * 60)
    
    # Set up MLflow
    mlflow.set_experiment("demandiq_xgboost")
    
    # Load features
    print(f"\nLoading features for top {limit_skus} SKUs...")
    df = load_features(limit_skus=limit_skus)
    
    # Get unique store-SKU combinations
    store_sku_combos = df.groupby(['store_id', 'sku']).size().reset_index()[['store_id', 'sku']]
    print(f"Training models for {len(store_sku_combos)} store-SKU combinations...")
    
    # Create models directory
    models_dir = Path('models/saved/xgboost')
    models_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for idx, row in store_sku_combos.iterrows():
        store_id = row['store_id']
        sku = row['sku']
        
        print(f"\n[{idx+1}/{len(store_sku_combos)}] Training: {store_id} - {sku}")
        
        # Prepare data
        X_train, X_test, y_train, y_test = prepare_training_data(df, store_id, sku)
        
        if X_train is None:
            print(f"  ✗ Skipped (insufficient data)")
            continue
        
        with mlflow.start_run(run_name=f"{store_id}_{sku}"):
            model, metrics = train_xgboost_model(X_train, X_test, y_train, y_test)
            
            # Log parameters and metrics
            mlflow.log_param("store_id", store_id)
            mlflow.log_param("sku", sku)
            mlflow.log_param("model_type", "xgboost")
            mlflow.log_metric("mae", metrics['mae'])
            mlflow.log_metric("rmse", metrics['rmse'])
            
            # Save model
            model_path = models_dir / f"{store_id}_{sku}_xgboost.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            mlflow.log_artifact(str(model_path))
            
            print(f"  ✓ MAE: {metrics['mae']:.2f}, RMSE: {metrics['rmse']:.2f}")
            
            results.append({
                'store_id': store_id,
                'sku': sku,
                'model_type': 'xgboost',
                'mae': metrics['mae'],
                'rmse': metrics['rmse'],
                'model_path': str(model_path)
            })
    
    # Save results summary
    results_df = pd.DataFrame(results)
    results_path = Path('models/saved/xgboost_results.csv')
    results_df.to_csv(results_path, index=False)
    
    print("\n" + "=" * 60)
    print(f"✓ XGBoost training complete!")
    print(f"  Trained {len(results)} models")
    print(f"  Average MAE: {results_df['mae'].mean():.2f}")
    print(f"  Average RMSE: {results_df['rmse'].mean():.2f}")
    print(f"  Results saved to: {results_path}")
    print("=" * 60)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--subset', type=int, default=10, help='Number of SKUs to train on')
    args = parser.parse_args()
    
    train_all_models(limit_skus=args.subset)
