
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.foodorder import FoodOrder
from app.models.inventory import InventoryTransaction, Location, LocationStock, InventoryItem
from sqlalchemy import desc

def check_deduction():
    db = SessionLocal()
    try:
        print("\n=== DEBUGGING FOOD ORDER INVENTORY DEDUCTION ===\n")

        # 1. Find Kitchen Location
        kitchen = db.query(Location).filter(Location.name.ilike("%Kitchen%")).first()
        if kitchen:
            print(f"Target Kitchen Location: '{kitchen.name}' (ID: {kitchen.id})")
        else:
            print("WARNING: No location found with 'Kitchen' in name.")

        # 2. Find Last Completed Food Order
        last_order = db.query(FoodOrder).filter(FoodOrder.status == 'completed').order_by(desc(FoodOrder.created_at)).first()
        
        if not last_order:
            print("No completed food orders found.")
            return

        print(f"\nLast Completed Order: ID {last_order.id}")
        print(f"Created At: {last_order.created_at}")
        
        # 3. Check Transactions for this Order
        print(f"\n--- Inventory Transactions for Order #{last_order.id} ---")
        transactions = db.query(InventoryTransaction).filter(
            InventoryTransaction.reference_number == f"ORD-{last_order.id}"
        ).all()

        if not transactions:
            print("No inventory transactions found for this order. (Maybe recipe not configured or deduction failed?)")
        
        for tx in transactions:
            item_name = tx.item.name if tx.item else "Unknown Item"
            print(f"\n[Transaction ID: {tx.id}]")
            print(f"  Item: {item_name} (ID: {tx.item_id})")
            print(f"  Qty Deducted: {tx.quantity}")
            print(f"  Notes: {tx.notes}") # Notes usually contain source info now
            
            # 4. Check Location Stock
            if kitchen:
                loc_stock = db.query(LocationStock).filter(
                    LocationStock.location_id == kitchen.id,
                    LocationStock.item_id == tx.item_id
                ).first()
                
                if loc_stock:
                    print(f"  -> Current Stock in '{kitchen.name}': {loc_stock.quantity}")
                    print(f"  -> Last Updated: {loc_stock.last_updated}")
                else:
                    print(f"  -> NO Stock Record found in '{kitchen.name}' for this item.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_deduction()
