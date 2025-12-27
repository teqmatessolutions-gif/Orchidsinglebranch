#!/usr/bin/env python3
"""Check if the latest purchase updated location stock"""

from app.database import SessionLocal
from app.models.inventory import PurchaseMaster, PurchaseDetail, LocationStock

db = SessionLocal()

# Get latest purchase
purchase = db.query(PurchaseMaster).order_by(PurchaseMaster.id.desc()).first()

if not purchase:
    print("No purchases found")
    db.close()
    exit()

print("=" * 60)
print(f"Latest Purchase: {purchase.purchase_number}")
print(f"Status: {purchase.status}")
print(f"Destination: {purchase.destination_location.name if purchase.destination_location else 'None'}")
print(f"Destination ID: {purchase.destination_location_id}")
print("=" * 60)

# Get purchase items
details = db.query(PurchaseDetail).filter(
    PurchaseDetail.purchase_master_id == purchase.id
).all()

print(f"\nPurchase Items: {len(details)}")
for d in details:
    item_name = d.item.name if d.item else f"Item #{d.item_id}"
    print(f"  - {item_name}: {d.quantity}")

# Check if items are in destination location
if purchase.destination_location_id:
    print(f"\nChecking location stock for: {purchase.destination_location.name}")
    
    for d in details:
        loc_stock = db.query(LocationStock).filter(
            LocationStock.location_id == purchase.destination_location_id,
            LocationStock.item_id == d.item_id
        ).first()
        
        item_name = d.item.name if d.item else f"Item #{d.item_id}"
        
        if loc_stock:
            print(f"  ✅ {item_name}: {loc_stock.quantity} in location")
        else:
            print(f"  ❌ {item_name}: NOT in location stock!")
            print(f"     💡 The server needs to restart to pick up the fix")
else:
    print("\n⚠️  No destination location set for this purchase")

db.close()
