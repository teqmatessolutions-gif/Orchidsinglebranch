
from app.database import SessionLocal
from app.models.inventory import InventoryItem, InventoryTransaction, PurchaseDetail, PurchaseMaster

def debug_tomato_stock():
    db = SessionLocal()
    print("--- Tracing Source of Tomatoes Stock ---")
    
    try:
        # Find the item
        tomato = db.query(InventoryItem).filter(InventoryItem.name.ilike("%Tomatoes%")).first()
        if not tomato:
            print("Item 'Fresh Tomatoes' not found.")
            return

        print(f"Item: {tomato.name}")
        print(f"Current Stock: {tomato.current_stock}")
        print(f"Unit Price: {tomato.unit_price}")
        print(f"Calculated Value: {tomato.current_stock * tomato.unit_price}")
        
        # Check Purchases
        print("\n[Purchases]")
        purchases = db.query(PurchaseDetail, PurchaseMaster).join(PurchaseMaster).filter(PurchaseDetail.item_id == tomato.id).all()
        if not purchases:
            print("No Purchase Orders found for this item.")
        else:
            for detail, master in purchases:
                print(f" - PO {master.purchase_number}: {detail.quantity} qty @ {detail.unit_price}")

        # Check Transactions (to see how stock entered)
        print("\n[Transaction History]")
        txns = db.query(InventoryTransaction).filter(InventoryTransaction.item_id == tomato.id).all()
        for txn in txns:
            print(f" - {txn.created_at} | {txn.transaction_type} | {txn.quantity} | {txn.notes}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_tomato_stock()
