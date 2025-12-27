import os
import sys
sys.path.insert(0, r'c:\releasing\orchid\ResortApp')

from app.database import SessionLocal
from app.models.inventory import LocationStock, InventoryItem
from app.models.room import Room
from datetime import datetime

db = SessionLocal()

try:
    # Find Room 102
    room = db.query(Room).filter(Room.number == "102").first()
    if not room or not room.inventory_location_id:
        print("Room 102 not found or has no inventory location")
        exit(1)
    
    print(f"Room 102 Location ID: {room.inventory_location_id}")
    
    # Get all stock items for this room
    stocks = db.query(LocationStock).join(InventoryItem).filter(
        LocationStock.location_id == room.inventory_location_id
    ).all()
    
    print(f"\nCurrent stock in Room 102:")
    for stock in stocks:
        print(f"  - {stock.item.name}: {stock.quantity} {stock.item.unit}")
    
    # Ask user which items to remove
    print("\nEnter item names to set to 0 (comma-separated), or 'all' for all items:")
    user_input = input("> ").strip()
    
    if user_input.lower() == 'all':
        for stock in stocks:
            if stock.quantity > 0:
                print(f"Setting {stock.item.name} from {stock.quantity} to 0")
                stock.quantity = 0
                stock.last_updated = datetime.utcnow()
    else:
        item_names = [name.strip() for name in user_input.split(',')]
        for stock in stocks:
            if stock.item.name in item_names and stock.quantity > 0:
                print(f"Setting {stock.item.name} from {stock.quantity} to 0")
                stock.quantity = 0
                stock.last_updated = datetime.utcnow()
    
    db.commit()
    print("\n✅ Stock updated successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
