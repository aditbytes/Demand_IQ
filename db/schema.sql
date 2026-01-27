-- DemandIQ PostgreSQL Database Schema

-- Drop existing tables (for clean setup)
DROP TABLE IF EXISTS reorders;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS forecast;
DROP TABLE IF EXISTS features;
DROP TABLE IF EXISTS sales;

-- Sales table: Historical sales transactions
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    store_id VARCHAR(20) NOT NULL,
    sku VARCHAR(50) NOT NULL,
    units INTEGER NOT NULL,
    price NUMERIC(10, 2),
    promo BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sales_store_sku ON sales(store_id, sku);
CREATE INDEX idx_sales_date ON sales(date);

-- Features table: Engineered features for ML models
CREATE TABLE features (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    store_id VARCHAR(20) NOT NULL,
    sku VARCHAR(50) NOT NULL,
    lag7 NUMERIC(10, 2),
    lag14 NUMERIC(10, 2),
    lag28 NUMERIC(10, 2),
    rolling7_mean NUMERIC(10, 2),
    rolling7_std NUMERIC(10, 2),
    rolling30_mean NUMERIC(10, 2),
    rolling30_std NUMERIC(10, 2),
    price NUMERIC(10, 2),
    price_change NUMERIC(10, 2),
    promo BOOLEAN,
    day_of_week INTEGER,
    month INTEGER,
    is_holiday BOOLEAN,
    is_snap BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_features_store_sku ON features(store_id, sku);
CREATE INDEX idx_features_date ON features(date);

-- Forecast table: ML model predictions
CREATE TABLE forecast (
    id SERIAL PRIMARY KEY,
    forecast_date DATE NOT NULL,
    store_id VARCHAR(20) NOT NULL,
    sku VARCHAR(50) NOT NULL,
    predicted_demand NUMERIC(10, 2) NOT NULL,
    model_name VARCHAR(50),
    confidence_lower NUMERIC(10, 2),
    confidence_upper NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_forecast_store_sku ON forecast(store_id, sku);
CREATE INDEX idx_forecast_date ON forecast(forecast_date);

-- Inventory table: Current stock levels
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(20) NOT NULL,
    sku VARCHAR(50) NOT NULL,
    current_stock INTEGER NOT NULL,
    lead_time INTEGER DEFAULT 7,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(store_id, sku)
);

CREATE INDEX idx_inventory_store_sku ON inventory(store_id, sku);

-- Reorders table: Reorder recommendations
CREATE TABLE reorders (
    id SERIAL PRIMARY KEY,
    store_id VARCHAR(20) NOT NULL,
    sku VARCHAR(50) NOT NULL,
    current_stock INTEGER,
    forecasted_demand NUMERIC(10, 2),
    safety_stock NUMERIC(10, 2),
    order_qty INTEGER NOT NULL,
    risk_level VARCHAR(10) CHECK (risk_level IN ('LOW', 'MED', 'HIGH')),
    recommendation_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reorders_store_sku ON reorders(store_id, sku);
CREATE INDEX idx_reorders_risk ON reorders(risk_level);

-- Grant permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON DATABASE demandiq TO your_username;
