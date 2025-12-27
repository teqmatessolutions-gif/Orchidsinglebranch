from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.room import Room
from app.models.inventory import Location, LocationStock, AssetRegistry, InventoryItem

from app.database import SessionLocal, engine

db = SessionLocal()

def check_room_inventory(room_number):
    print(f"Checking inventory for Room {room_number}...")
    
    # 1. Get Room
    room = db.query(Room).filter(Room.number == room_number).first()
    if not room:
        print(f"Room {room_number} not found!")
        return

    print(f"Room ID: {room.id}")
    print(f"Inventory Location ID: {room.inventory_location_id}")

    if not room.inventory_location_id:
        print("WARNING: No Inventory Location ID assigned to this room!")
        # Try to find a location that might match by name
        potential_loc = db.query(Location).filter(Location.name.like(f"%{room_number}%")).first()
        if potential_loc:
            print(f"Found potential location match by name: {potential_loc.name} (ID: {potential_loc.id})")
        return

    location = db.query(Location).filter(Location.id == room.inventory_location_id).first()
    print(f"Location: {location.name} (ID: {location.id})")

    # 2. Check Location Stock (Consumables)
    stocks = db.query(LocationStock).filter(LocationStock.location_id == room.inventory_location_id).all()
    print(f"\n--- Location Stock ({len(stocks)}) ---")
    for stock in stocks:
        item = db.query(InventoryItem).get(stock.item_id)
        print(f"- {item.name}: {stock.quantity} {item.unit}")

    # 4. Check Available Inventory Items
    print(f"\n--- Available Inventory Items (First 10) ---")
    items = db.query(InventoryItem).limit(10).all()
    for item in items:
        cat_name = item.category.name if item.category else "No Category"
        print(f"- {item.name} (ID: {item.id}, Category: {cat_name}, Stock: {item.current_stock})")

if __name__ == "__main__":
    check_room_inventory("106")
