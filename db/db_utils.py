"""
Database utility functions for DemandIQ
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'demandiq')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_engine():
    """Create and return SQLAlchemy engine"""
    return create_engine(DATABASE_URL, pool_pre_ping=True)

def get_session():
    """Create and return database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def test_connection():
    """Test database connection"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            print(f"✓ Successfully connected to database: {DB_NAME}")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
