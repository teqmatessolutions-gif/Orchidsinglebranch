from app.database import SessionLocal
from app.models.inventory import InventoryTransaction

db = SessionLocal()
try:
    # Check for transfer_in transactions
    transfer_in = db.query(InventoryTransaction).filter(
        InventoryTransaction.transaction_type == "transfer_in"
    ).all()
    
    print(f"Total transfer_in transactions: {len(transfer_in)}\n")
    
    for txn in transfer_in:
        print(f"ID: {txn.id}")
        print(f"Item ID: {txn.item_id}")
        print(f"Quantity: {txn.quantity}")
        print(f"Reference: {txn.reference_number}")
        print(f"Department: {txn.department}")
        print(f"Notes: {txn.notes}")
        print(f"Created: {txn.created_at}")
        print("-" * 60)
        
finally:
    db.close()
