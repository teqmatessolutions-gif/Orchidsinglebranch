from app.database import SessionLocal
from app.models.inventory import PurchaseMaster, LocationStock, InventoryItem, InventoryTransaction

db = SessionLocal()

# Get the latest purchase
p = db.query(PurchaseMaster).order_by(PurchaseMaster.id.desc()).first()

print(f"=== Latest Purchase ===")
print(f"PO Number: {p.purchase_number}")
print(f"Status: {p.status}")
print(f"Destination Location ID: {p.destination_location_id}")
print(f"Details count: {len(p.details)}")

for d in p.details:
    print(f"\n  Detail: Item ID {d.item_id}, Qty: {d.quantity}, Price: {d.unit_price}")
    
    # Check if item exists
    item = db.query(InventoryItem).filter(InventoryItem.id == d.item_id).first()
    if item:
        print(f"    Item: {item.name}, Current Stock: {item.current_stock}")
    else:
        print(f"    Item NOT FOUND!")

# Check location stocks
if p.destination_location_id:
    stocks = db.query(LocationStock).filter(
        LocationStock.location_id == p.destination_location_id
    ).all()
    print(f"\n=== Location Stocks (Location {p.destination_location_id}) ===")
    print(f"Total stocks: {len(stocks)}")
    for s in stocks:
        print(f"  Item {s.item_id}: {s.quantity}")

# Check transactions
transactions = db.query(InventoryTransaction).filter(
    InventoryTransaction.reference_number == p.purchase_number
).all()
print(f"\n=== Transactions for {p.purchase_number} ===")
print(f"Total transactions: {len(transactions)}")
for t in transactions:
    print(f"  Item {t.item_id}, Type: {t.transaction_type}, Qty: {t.quantity}")

db.close()
