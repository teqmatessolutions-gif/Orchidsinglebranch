from app.database import SessionLocal
from app.models.inventory import InventoryItem, InventoryCategory

def check_towel_data():
    db = SessionLocal()
    try:
        # Search for "Kitchen Hand Towel" or similar
        items = db.query(InventoryItem).filter(InventoryItem.name.ilike("%Kitchen Hand Towel%")).all()
        
        if not items:
            print("No item found matching 'Kitchen Hand Towel'")
            return

        for item in items:
            print(f"--- Item: {item.name} (ID: {item.id}) ---")
            print(f"Category: {item.category.name if item.category else 'None'} (ID: {item.category_id})")
            print(f"track_laundry_cycle: {item.track_laundry_cycle}")
            print(f"is_rentable (derived): {True if (item.category and 'rental' in (item.category.name or '').lower()) else False}")
            print(f"is_fixed_asset: {item.is_fixed_asset}")
            
            # Check raw category to be sure
            if item.category:
                print(f"Category track_laundry: {item.category.track_laundry}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_towel_data()
