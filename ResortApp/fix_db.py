import sys
import os
from sqlalchemy import create_engine, text

# Add current directory to path to allow imports
sys.path.append(os.getcwd())

try:
    from app.database import SQLALCHEMY_DATABASE_URL
except ImportError:
    # Fallback if app.database cannot be imported
    print("Could not import app.database, using default sqlite")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./orchid.db"

def fix_database():
    print(f"Connecting to database: {SQLALCHEMY_DATABASE_URL}")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            print("Attempting to add payment_method column to purchase_masters...")
            conn.execute(text("ALTER TABLE purchase_masters ADD COLUMN payment_method VARCHAR"))
            conn.commit()
            print("Successfully added payment_method column.")
        except Exception as e:
            print(f"Error (column might already exist): {e}")

if __name__ == "__main__":
    fix_database()
