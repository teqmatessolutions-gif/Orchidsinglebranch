from app.database import SessionLocal
from app.models.inventory import InventoryItem

db = SessionLocal()

# Check for Mineral Water
items = db.query(InventoryItem).filter(InventoryItem.name.ilike("%Mineral Water%")).all()
if not items:
    print("Mineral Water not found!")
else:
    for item in items:
        print(f"Item: {item.name}")
        print(f"  ID: {item.id}")
        print(f"  Unit Price (Cost): {item.unit_price}")
        print(f"  Selling Price: {item.selling_price}")
        print(f"  Complimentary Limit: {item.complimentary_limit}")

# Check for Coca Cola
items = db.query(InventoryItem).filter(InventoryItem.name.ilike("%Coca%")).all()
if not items:
    print("Coca Cola not found!")
else:
    for item in items:
        print(f"Item: {item.name}")
        print(f"  ID: {item.id}")
        print(f"  Unit Price (Cost): {item.unit_price}")
        print(f"  Selling Price: {item.selling_price}")
        print(f"  Complimentary Limit: {item.complimentary_limit}")

# Check for Walkie Talkie
items = db.query(InventoryItem).filter(InventoryItem.name.ilike("%Walkie%")).all()
if not items:
    print("Walkie Talkie not found!")
else:
    for item in items:
        print(f"Item: {item.name}")
        print(f"  Is Fixed Asset: {item.is_asset_fixed}")
        print(f"  Is Sellable to Guest: {item.is_sellable_to_guest}")
        print(f"  Is Perishable: {item.is_perishable}")

# Check for Rice
items = db.query(InventoryItem).filter(InventoryItem.name.ilike("%Rice%")).all()
if not items:
    print("Rice not found!")
else:
    for item in items:
        print(f"Item: {item.name}")
        print(f"  Is Fixed Asset: {item.is_asset_fixed}")
        print(f"  Is Sellable to Guest: {item.is_sellable_to_guest}")
        print(f"  Is Perishable: {item.is_perishable}")

db.close()
