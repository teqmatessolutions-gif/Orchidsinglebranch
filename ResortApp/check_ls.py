import sys
import os

sys.path.append(os.getcwd())
try:
    from app.database import SessionLocal
    from app.models.inventory import LocationStock
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'ResortApp'))
    from app.database import SessionLocal
    from app.models.inventory import LocationStock

def check():
    db = SessionLocal()
    try:
        print("Checking LocationStock ID 74 (Item 19)...")
        ls = db.query(LocationStock).filter(LocationStock.id == 74).first()
        if ls:
            print(f"LS 74 Quantity: {ls.quantity}")
        else:
            print("LS 74 not found")
    finally:
        db.close()

if __name__ == "__main__":
    check()
