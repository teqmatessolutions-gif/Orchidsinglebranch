
import sys
import os
from sqlalchemy import func

# Add root directory to path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models.inventory import InventoryItem, InventoryTransaction

def check_stock():
    db = SessionLocal()
    try:
        search_terms = ["Mineral Water", "Coca Cola"]
        items = []
        for term in search_terms:
            found_items = db.query(InventoryItem).filter(InventoryItem.name.ilike(f"%{term}%")).all()
            items.extend(found_items)

        if not items:
            print("No items found matching 'Mineral Water' or 'Coca Cola'")
            return

        print(f"{'Item Name':<30} | {'ID':<5} | {'Current Stock':<15} | {'Unit'}")
        print("-" * 70)
        
        for item in items:
            print(f"{item.name:<30} | {item.id:<5} | {item.current_stock:<15} | {item.unit}")
            
            # Analyze transactions
            txns = db.query(InventoryTransaction).filter(InventoryTransaction.item_id == item.id).all()
            print(f"\n--- Transactions for {item.name} ---")
            
            calc_stock = 0
            for txn in txns:
                qty = txn.quantity
                
                # Determine sign based on transaction type
                # This logic might need adjustment based on how the system is actually verified
                sign = 0
                if txn.transaction_type in ['in', 'purchase', 'checkin', 'stock received', 'transfer_in']:
                    sign = 1
                elif txn.transaction_type in ['out', 'issue', 'waste', 'checkout', 'transfer_out']:
                    sign = -1
                else:
                    print(f"  [WARNING] Unknown transaction type: {txn.transaction_type}")
                
                change = qty * sign
                calc_stock += change
                print(f"  Type: {txn.transaction_type:<15} | Qty: {qty:<10} | Change: {change:<10} | Date: {txn.created_at}")

            print(f"  > Transaction Sum (Calculated): {calc_stock}")
            print(f"  > Current Stock (In DB):        {item.current_stock}")
            
            # Check Purchase Details to see where it went
            from app.models.inventory import PurchaseMaster, PurchaseDetail
            purchases = db.query(PurchaseDetail).filter(PurchaseDetail.item_id == item.id).all()
            for p in purchases:
               pm = db.query(PurchaseMaster).filter(PurchaseMaster.id == p.purchase_master_id).first()
               if pm:
                   print(f"  > Purchase found: ID {pm.id}, Status: {pm.status}, Dest Loc: {pm.destination_location_id}, Qty: {p.quantity}")
            
            # Check Location Stocks
            from app.models.inventory import LocationStock
            loc_stocks = db.query(LocationStock).filter(LocationStock.item_id == item.id).all()
            if loc_stocks:
                print(f"  > Location Stocks:")
                loc_sum = 0
                for ls in loc_stocks:
                    print(f"    - Loc ID {ls.location_id}: {ls.quantity}")
                    loc_sum += ls.quantity
                print(f"    - Sum of Location Stocks: {loc_sum}")
            else:
                print(f"  > No LocationStock records found.")
            
            print("-" * 70)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    # Redirect stdout to a file with utf-8 encoding
    with open("stock_report.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        check_stock()
        sys.stdout = sys.__stdout__
    
    # Print content of the file to console for viewing
    with open("stock_report.txt", "r", encoding="utf-8") as f:
        print(f.read())
