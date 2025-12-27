
from app.database import SessionLocal
from app.models.inventory import InventoryItem, InventoryTransaction, PurchaseMaster

def check():
    db = SessionLocal()
    try:
        item = db.query(InventoryItem).filter(InventoryItem.name.ilike("%Basmati%")).first()
        if not item:
            print("Item not found")
            return

        print(f"Item: {item.name}, ID: {item.id}, Current Stock: {item.current_stock}")

        txns = db.query(InventoryTransaction).filter(InventoryTransaction.item_id == item.id).order_by(InventoryTransaction.created_at).all()
        
        print("\n--- Transactions ---")
        running_stock = 0
        for t in txns:
            # Determine sign
            change = t.quantity
            if t.transaction_type in ['out', 'transfer_out']:
                change = -change
            
            # Note: The logic in my frontend code handles types specifically.
            # 'in' (purchase), 'adjustment', 'transfer_in' -> positive?
            # 'out', 'transfer_out' -> negative?
            
            running_stock += change # rough calc
            
            print(f"ID: {t.id} | Date: {t.created_at} | Type: {t.transaction_type} | Qty: {t.quantity} | Ref: {t.reference_number}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
