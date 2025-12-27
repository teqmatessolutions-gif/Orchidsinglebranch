from app.database import SessionLocal
from app.models.inventory import InventoryTransaction

db = SessionLocal()
try:
    # Check all transactions for ISS-20251209-001
    txns = db.query(InventoryTransaction).filter(
        InventoryTransaction.reference_number == 'ISS-20251209-001'
    ).all()
    
    print(f"Total transactions for ISS-20251209-001: {len(txns)}\n")
    
    for txn in txns:
        print(f"Type: {txn.transaction_type}")
        print(f"Item ID: {txn.item_id}")
        print(f"Quantity: {txn.quantity}")
        print(f"Department: {txn.department}")
        print(f"Notes: {txn.notes}")
        print("-" * 50)
        
finally:
    db.close()
