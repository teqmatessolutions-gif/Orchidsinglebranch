import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text
from app.database import SessionLocal

def check_checkouts():
    db = SessionLocal()
    try:
        # Check if table exists
        # In some setups, table names might be singular or plural or capitalized.
        # SQLAlchemy models usually define __tablename__. 
        # Checkout model is likely 'checkouts'.
        
        result = db.execute(text("SELECT count(*) FROM checkouts")).scalar()
        print(f"Total checkouts in DB: {result}")
        
        if result > 0:
            rows = db.execute(text("SELECT id, room_number, guest_name, grand_total, created_at FROM checkouts ORDER BY id DESC LIMIT 5")).fetchall()
            print("Recent checkouts:")
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Error: {e}")
        # Try finding the table name if that failed
        try:
             result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%checkout%'")).fetchall()
             print(f"Tables matching 'checkout': {result}")
        except:
             pass
    finally:
        db.close()

if __name__ == "__main__":
    check_checkouts()
