"""
Model Evaluation and Selection
Compares baseline, Prophet, and XGBoost to select best model per SKU
"""
import pandas as pd
import numpy as np
from pathlib import Path


def load_sales_data():
    """Load sales data from CSV"""
    csv_path = Path('data/processed/sales_cleaned.csv')
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Sales data not found at {csv_path}. Run clean.py first.")
    
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def baseline_forecast(df, store_id, sku):
    """Baseline model: last week's sales = this week's forecast"""
    df_sku = df[(df['store_id'] == store_id) & (df['sku'] == sku)].copy()
    df_sku = df_sku.sort_values('date')
    
    if len(df_sku) < 14:
        return None
    
    # Use last 7 days as forecast
    last_7_days = df_sku.tail(7)['units'].values
    forecast = last_7_days
    
    # Calculate MAE on validation period (compare week N-1 to week N-2)
    if len(df_sku) >= 21:
        actual_week = df_sku.iloc[-14:-7]['units'].values
        predicted_week = df_sku.iloc[-21:-14]['units'].values
        mae = np.mean(np.abs(actual_week - predicted_week))
    else:
        mae = df_sku['units'].std()  # Fallback to std dev
    
    return {
        'model': 'baseline',
        'mae': mae,
        'forecast': forecast
    }

def load_model_results():
    """Load results from Prophet and XGBoost training"""
    results = {}
    
    # Prophet results
    prophet_path = Path('models/saved/prophet_results.csv')
    if prophet_path.exists():
        prophet_df = pd.read_csv(prophet_path)
        for _, row in prophet_df.iterrows():
            key = (row['store_id'], row['sku'])
            results[key] = {
                'prophet': {
                    'mae': row['mae'],
                    'model_path': row['model_path']
                }
            }
    
    # XGBoost results
    xgboost_path = Path('models/saved/xgboost_results.csv')
    if xgboost_path.exists():
        xgboost_df = pd.read_csv(xgboost_path)
        for _, row in xgboost_df.iterrows():
            key = (row['store_id'], row['sku'])
            if key not in results:
                results[key] = {}
            results[key]['xgboost'] = {
                'mae': row['mae'],
                'rmse': row['rmse'],
                'model_path': row['model_path']
            }
    
    return results

def evaluate_and_select():
    """Evaluate all models and select best per SKU"""
    print("=" * 60)
    print("DemandIQ - Model Evaluation & Selection")
    print("=" * 60)
    
    # Load sales data from CSV
    df = load_sales_data()
    
    # Load Prophet and XGBoost results
    model_results = load_model_results()
    
    if len(model_results) == 0:
        print("\n✗ No model results found. Run train_prophet.py and train_xgboost.py first.")
        return
    
    print(f"\nEvaluating models for {len(model_results)} store-SKU combinations...")
    
    comparison_results = []
    
    for idx, (key, models) in enumerate(model_results.items()):
        store_id, sku = key
        
        print(f"\n[{idx+1}/{len(model_results)}] Evaluating: {store_id} - {sku}")
        
        # Baseline
        baseline_result = baseline_forecast(df, store_id, sku)
        
        if baseline_result is None:
            continue
        
        # Compare MAE across all models
        model_comparison = {
            'store_id': store_id,
            'sku': sku,
            'baseline_mae': baseline_result['mae']
        }
        
        if 'prophet' in models:
            model_comparison['prophet_mae'] = models['prophet']['mae']
        
        if 'xgboost' in models:
            model_comparison['xgboost_mae'] = models['xgboost']['mae']
        
        # Select best model (lowest MAE)
        mae_scores = {
            'baseline': baseline_result['mae'],
            'prophet': models.get('prophet', {}).get('mae', float('inf')),
            'xgboost': models.get('xgboost', {}).get('mae', float('inf'))
        }
        
        best_model = min(mae_scores, key=mae_scores.get)
        best_mae = mae_scores[best_model]
        
        model_comparison['best_model'] = best_model
        model_comparison['best_mae'] = best_mae
        
        print(f"  Baseline MAE: {baseline_result['mae']:.2f}")
        if 'prophet' in models:
            print(f"  Prophet MAE: {models['prophet']['mae']:.2f}")
        if 'xgboost' in models:
            print(f"  XGBoost MAE: {models['xgboost']['mae']:.2f}")
        print(f"  ✓ Best model: {best_model.upper()} (MAE: {best_mae:.2f})")
        
        comparison_results.append(model_comparison)
    
    # Save comparison results
    results_df = pd.DataFrame(comparison_results)
    output_path = Path('models/saved/model_comparison.csv')
    results_df.to_csv(output_path, index=False)
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("Model Selection Summary")
    print("=" * 60)
    print(f"\nTotal SKUs evaluated: {len(results_df)}")
    print(f"\nModel selection breakdown:")
    print(results_df['best_model'].value_counts())
    print(f"\nAverage MAE by model:")
    for model in ['baseline', 'prophet', 'xgboost']:
        col = f'{model}_mae'
        if col in results_df.columns:
            avg_mae = results_df[col].mean()
            print(f"  {model.capitalize()}: {avg_mae:.2f}")
    
    print(f"\n✓ Results saved to: {output_path}")
    print("=" * 60)

if __name__ == '__main__':
    evaluate_and_select()
