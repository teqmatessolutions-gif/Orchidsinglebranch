
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add root directory to path
sys.path.append(os.getcwd())

from app.database import Base
from app.models.foodorder import FoodOrder

# Setup DB
from app.database import SQLALCHEMY_DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_food_orders():
    db = SessionLocal()
    try:
        print("--- Checking Food Orders ---")
        orders = db.query(FoodOrder).all()
        print(f"Total Food Orders Found: {len(orders)}")
        for o in orders:
            print(f"ID: {o.id} | Status: {o.status} | Billing: {o.billing_status} | Amount: {o.amount}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_food_orders()
