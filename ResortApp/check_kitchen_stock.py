#!/usr/bin/env python3
"""Check recent purchases and kitchen location stocks"""

from app.database import SessionLocal
from app.models.inventory import PurchaseMaster, PurchaseDetail, LocationStock, Location

db = SessionLocal()

print("=" * 60)
print("Recent Purchases:")
print("=" * 60)

purchases = db.query(PurchaseMaster).order_by(PurchaseMaster.id.desc()).limit(5).all()

for p in purchases:
    dest_name = p.destination_location.name if p.destination_location else "No location"
    print(f"\n📦 PO-{p.purchase_number}")
    print(f"   Status: {p.status}")
    print(f"   Destination: {dest_name}")
    print(f"   Date: {p.purchase_date}")
    
    # Show items
    details = db.query(PurchaseDetail).filter(PurchaseDetail.purchase_master_id == p.id).all()
    if details:
        print(f"   Items:")
        for d in details:
            item_name = d.item.name if d.item else f"Item #{d.item_id}"
            print(f"      - {item_name}: {d.quantity} {d.unit}")

print("\n" + "=" * 60)
print("Main Kitchen Location Stocks:")
print("=" * 60)

kitchen = db.query(Location).filter(Location.name.ilike('%kitchen%')).first()

if kitchen:
    print(f"\n🏪 Location: {kitchen.name} (ID: {kitchen.id})")
    stocks = db.query(LocationStock).filter(LocationStock.location_id == kitchen.id).all()
    
    if stocks:
        print(f"   Items in stock: {len(stocks)}")
        for s in stocks:
            item_name = s.item.name if s.item else f"Item #{s.item_id}"
            print(f"      - {item_name}: {s.quantity}")
    else:
        print("   ⚠️  No items in this location!")
        print("   💡 Tip: You need to RECEIVE the purchase to add items to location stock")
else:
    print("   ❌ Kitchen location not found")

db.close()
