from app.database import SessionLocal
from app.models.inventory import LocationStock, Location

db = SessionLocal()
try:
    print("Location Stock Distribution:")
    print("=" * 80)
    
    # Get all location stocks for the transferred items
    loc_stocks = db.query(LocationStock).filter(
        LocationStock.item_id.in_([3, 7, 11])
    ).all()
    
    for ls in loc_stocks:
        location = db.query(Location).filter(Location.id == ls.location_id).first()
        loc_name = f"{location.building} - {location.room_area}" if location else f"Location #{ls.location_id}"
        
        print(f"\nItem ID: {ls.item_id}")
        print(f"Location: {loc_name}")
        print(f"Quantity: {ls.quantity}")
        print(f"Last Updated: {ls.last_updated}")
        print("-" * 80)
        
finally:
    db.close()
