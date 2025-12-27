import sys
import os
import traceback

sys.path.append(os.getcwd())
from app.database import SessionLocal
from app.models.inventory import PurchaseMaster, LocationStock, InventoryItem

def fix_and_debug_stock():
    db = SessionLocal()
    try:
        print("--- Fixing/Debugging Location Stock ---")
        
        # Get latest purchase
        created = db.query(PurchaseMaster).order_by(PurchaseMaster.id.desc()).first()
        if not created: 
            print("No purchase found.")
            return

        print(f"Purchase {created.id} (Location: {created.destination_location_id})")
        
        for detail in created.details:
            if not created.destination_location_id:
                print("No location ID. Skipping.")
                continue

            # Check/Create Location Stock
            ls = db.query(LocationStock).filter(
                LocationStock.location_id == created.destination_location_id,
                LocationStock.item_id == detail.item_id
            ).first()
            
            if not ls:
                print(f"MISSING STOCK DETECTED for Item {detail.item_id}. Creating...")
                ls = LocationStock(
                    location_id=created.destination_location_id,
                    item_id=detail.item_id,
                    quantity=detail.quantity
                )
                db.add(ls)
                try:
                    db.commit()
                    print("SUCCESS: Stock created.")
                except Exception as e:
                    print(f"COMMIT FAILED: {e}")
                    traceback.print_exc()
            else:
                print(f"Stock exists ({ls.quantity}). No action needed.")

    except Exception as e:
        print(f"General Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_and_debug_stock()
