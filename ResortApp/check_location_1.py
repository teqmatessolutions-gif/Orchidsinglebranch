"""
Check if location ID 1 exists (Central Warehouse)
"""
from app.database import SessionLocal
from app.models.inventory import Location

def check_location_1():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("CHECKING LOCATION ID 1 (Central Warehouse)")
        print("=" * 70)
        
        loc = db.query(Location).filter(Location.id == 1).first()
        
        if loc:
            print(f"\n✅ Location ID 1 exists:")
            print(f"  Name: {loc.name}")
            print(f"  Building: {loc.building}")
            print(f"  Room Area: {loc.room_area}")
            print(f"  Type: {loc.location_type}")
            print(f"  Active: {loc.is_active}")
        else:
            print("\n❌ Location ID 1 does NOT exist!")
            print("\nThis is the problem! The code assumes location ID 1 is the Central Warehouse.")
            print("\nLet's check what locations DO exist:")
            
            all_locs = db.query(Location).limit(10).all()
            print(f"\nFirst 10 locations:")
            for l in all_locs:
                print(f"  ID {l.id}: {l.building} - {l.room_area} ({l.location_type})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_location_1()
