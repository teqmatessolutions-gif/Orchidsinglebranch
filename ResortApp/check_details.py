import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import text
from app.database import SessionLocal

def check_checkouts_detailed():
    db = SessionLocal()
    try:
        # Select all columns used in CheckoutFull
        columns = [
            "id", "booking_id", "package_booking_id", "room_total", "food_total", 
            "service_total", "package_total", "tax_amount", "discount_amount", 
            "grand_total", "payment_method", "payment_status", "created_at", 
            "guest_name", "room_number"
        ]
        query = f"SELECT {', '.join(columns)} FROM checkouts ORDER BY id DESC LIMIT 1"
        row = db.execute(text(query)).fetchone()
        
        if row:
            print("Row data:")
            # dict(row) might not work directly with recent sqlalchemy, use _mapping
            try:
                data = dict(row._mapping)
            except:
                data = dict(row)
            
            for k, v in data.items():
                print(f"{k}: {v} (Type: {type(v)})")
        else:
            print("No checkouts found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_checkouts_detailed()
