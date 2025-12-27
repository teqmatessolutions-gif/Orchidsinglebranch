"""
Quick fix for asset mapping - Check if location exists before creating stock issue
"""
from app.database import SessionLocal
from app.models.inventory import Location

def check_location():
    db = SessionLocal()
    
    try:
        # Check location ID 102 (Main Building - Room 102)
        # Based on the screenshot, this is the location being used
        
        # First, let's see all locations
        locations = db.query(Location).all()
        
        print("=" * 70)
        print("ALL LOCATIONS IN DATABASE")
        print("=" * 70)
        
        for loc in locations:
            print(f"ID: {loc.id}, Building: {loc.building}, Room: {loc.room_area}, Type: {loc.location_type}")
        
        print()
        print("=" * 70)
        
        # Now check if there's a location with "Room 102"
        room_102 = db.query(Location).filter(
            Location.room_area.ilike("%102%")
        ).all()
        
        if room_102:
            print("Found Room 102:")
            for loc in room_102:
                print(f"  ID: {loc.id}")
                print(f"  Building: {loc.building}")
                print(f"  Room Area: {loc.room_area}")
                print(f"  Type: {loc.location_type}")
                print(f"  Active: {loc.is_active}")
                # Check if it has any unexpected fields
                print(f"  All attributes: {dir(loc)}")
        else:
            print("Room 102 not found!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_location()
