
from app.database import SessionLocal
from app.models.inventory import InventoryItem, InventoryTransaction

db = SessionLocal()

item_name = "Basmati Rice Premium Grade"
item = db.query(InventoryItem).filter(InventoryItem.name == item_name).first()

if not item:
    print(f"Item '{item_name}' not found!")
else:
    print(f"Item: {item.name}, Current Stock: {item.current_stock}, ID: {item.id}")
    
    print("\n--- Transactions ---")
    txns = db.query(InventoryTransaction).filter(InventoryTransaction.item_id == item.id).order_by(InventoryTransaction.created_at).all()
    for txn in txns:
        print(f"ID: {txn.id}, Type: {txn.transaction_type}, Qty: {txn.quantity}, Date: {txn.created_at}, Ref: {txn.reference_number}, Notes: {txn.notes}")

