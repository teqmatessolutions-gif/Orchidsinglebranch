
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.inventory import InventoryItem, StockIssueDetail, StockIssue
from app.models.checkout import CheckoutRequest
from app.api.checkout import get_checkout_request_inventory_details
from app.models.user import User
import json

def debug_full_context():
    db = SessionLocal()
    try:
        # 1. Search for potential duplicate items
        print("\n=== SEARCHING FOR ITEM 'Coca' ===")
        items = db.query(InventoryItem).filter(InventoryItem.name.ilike("%Coca%")).all()
        for i in items:
            print(f"Item ID: {i.id} | Name: {i.name} | Category: {i.category.name if i.category else 'None'} | Laundry: {i.track_laundry_cycle} | Fixed: {i.is_asset_fixed}")
            
            # Check issues for this item
            issues = db.query(StockIssueDetail).filter(StockIssueDetail.item_id == i.id).count()
            print(f"  -> Total Stock Issues: {issues}")

        # 2. Find an active Checkout Request to simulate
        print("\n=== FINDING ACTIVE CHECKOUT REQUEST ===")
        # Look for a pending or inventory_checked request
        req = db.query(CheckoutRequest).order_by(CheckoutRequest.id.desc()).first()
        
        if req:
            print(f"Using Checkout Request ID: {req.id} for Room {req.room_number}")
            
            # Mock User - SQLAlchemy expects a persistent object for relationships if accessed, 
            # but API might just check attributes. 
            # The error 'str' object has no attribute '_sa_instance_state' usually comes from passing a string where an object is expected,
            # OR from the session not attaching the object.
            # Let's try fetching a real user.
            user = db.query(User).first()
            if not user:
                 print("No user found in DB, authentication might fail logic")
            else:
                 print(f"Using User: {user.name}")
            data = get_checkout_request_inventory_details(req.id, db, user)
            
            # Filter specifically for Coca Cola in the response
            print("\n=== API RESPONSE ITEMS (Filtered for 'Coca') ===")
            found = False
            for item in data.get("items", []):
                if "coca" in item["item_name"].lower():
                    found = True
                    print(json.dumps(item, indent=2))
            
            if not found:
                print("No 'Coca' items found in this checkout request's returned items.")
                # Print ALL items briefly to see what's there
                print("\n=== ALL ITEMS IN RESPONSE ===")
                for item in data.get("items", []):
                    print(f"- {item['item_name']} (Rentable: {item.get('is_rentable')}, Fixed: {item.get('is_fixed_asset')})")

        else:
            print("No active checkout requests found.")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_full_context()
