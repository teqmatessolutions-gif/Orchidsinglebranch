from app.utils.auth import get_db
from app.models.inventory import InventoryItem, LocationStock, Location
db = next(get_db())

# Search for the item
item = db.query(InventoryItem).filter(InventoryItem.name.like("%Mineral Water%")).first()

if not item:
    print("Item 'Mineral Water' not found!")
else:
    print(f"Item: {item.name} | ID: {item.id} | Global Current Stock: {item.current_stock}")
    
    # Check Location Stocks
    stocks = db.query(LocationStock).filter(LocationStock.item_id == item.id).all()
    
    if not stocks:
        print("No LocationStock records found for this item.")
    else:
        print(f"Found {len(stocks)} LocationStock records:")
        for s in stocks:
            loc = db.query(Location).filter(Location.id == s.location_id).first()
            loc_name = loc.name if loc else "Unknown Location"
            loc_type = loc.location_type if loc else "Unknown Type"
            print(f" - Location: {loc_name} (ID: {s.location_id}, Type: {loc_type}) => Quantity: {s.quantity}")
