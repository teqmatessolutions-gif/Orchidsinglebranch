import requests
import sys
import os
import datetime

sys.path.append(os.getcwd())
try:
    from app.database import SessionLocal
    from app.models.inventory import Vendor, LocationStock
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'ResortApp'))
    from app.database import SessionLocal
    from app.models.inventory import Vendor, LocationStock

def run_test():
    # Phase 1: Snapshot
    db = SessionLocal()
    try:
        item_id = 20
        loc_id = 14
        ls = db.query(LocationStock).filter(LocationStock.location_id==loc_id, LocationStock.item_id==item_id).first()
        before = ls.quantity if ls else 0.0
        print(f"Stock Before: {before}")
        vendor_id = db.query(Vendor).first().id
    finally:
        db.close()
        
    # Phase 2: Action
    payload = {
        "purchase_number": f"FIXTEST-V2-{datetime.datetime.now().strftime('%M%S')}",
        "vendor_id": vendor_id,
        "purchase_date": datetime.date.today().isoformat(),
        "status": "received",
        "destination_location_id": loc_id,
        "details": [{"item_id": item_id, "quantity": 5, "unit_price": 10, "unit": "pcs"}]
    }
    
    # Token
    db = SessionLocal()
    from app.models.user import User
    from app.utils.auth import create_access_token
    user = db.query(User).first()
    token = create_access_token(data={"user_id": user.id, "role": user.role.name if user.role else 'admin'})
    db.close()
    
    print("Sending API Request...")
    r = requests.post("http://127.0.0.1:8011/api/inventory/purchases", json=payload, headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200: 
        print(f"API Error: {r.text}")
        return

    # Phase 3: Verify
    db = SessionLocal()
    try:
        ls = db.query(LocationStock).filter(LocationStock.location_id==loc_id, LocationStock.item_id==item_id).first()
        after = ls.quantity if ls else 0.0
        print(f"Stock After: {after}")
        
        if abs(after - (before + 5)) < 0.1:
            print("SUCCESS: Stock Updated.")
        else:
            print("FAILURE: Stock did not update.")
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
