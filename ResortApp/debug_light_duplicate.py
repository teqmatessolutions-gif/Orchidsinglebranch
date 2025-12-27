from app.database import SessionLocal
from app.models.inventory import InventoryItem, AssetMapping, AssetRegistry, LocationStock

db = SessionLocal()

print("--- Checking Items named 'light' ---")
items = db.query(InventoryItem).filter(InventoryItem.name.ilike("%light%")).all()
for item in items:
    print(f"ID: {item.id}, Name: {item.name}, Is Asset: {item.is_asset_fixed}, Is Consumable (implied): {not item.is_asset_fixed}")

print("\n--- Checking Asset Mappings for Room 101 (LOC-RM-101) ---")
# Assuming we can find Room 101's location ID
from app.models.inventory import Location
room_101 = db.query(Location).filter(Location.name == "Room 101").first()

if room_101:
    print(f"Room 101 ID: {room_101.id}")
    
    # Check Asset Mappings (Legacy)
    mappings = db.query(AssetMapping).filter(AssetMapping.location_id == room_101.id).all()
    print(f"Asset Mappings count: {len(mappings)}")
    for m in mappings:
        print(f"  Mapping: Item ID {m.item_id} ({m.item.name}), Qty: {m.quantity}")

    # Check Asset Registry (New)
    registry = db.query(AssetRegistry).filter(AssetRegistry.current_location_id == room_101.id).all()
    print(f"Asset Registry count: {len(registry)}")
    for r in registry:
        print(f"  Registry: Item ID {r.item_id} ({r.item.name}), Tag: {r.asset_tag_id}")

    # Check Location Stock
    stocks = db.query(LocationStock).filter(LocationStock.location_id == room_101.id).all()
    print(f"Location Stock count: {len(stocks)}")
    for s in stocks:
        print(f"  Stock: Item ID {s.item_id} ({s.item.name}), Qty: {s.quantity}")

else:
    print("Room 101 not found")

db.close()
