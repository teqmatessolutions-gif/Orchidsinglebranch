"""
Check Coca Cola and Mineral Water stock levels
"""
from app.database import SessionLocal
from app.models.inventory import InventoryItem, LocationStock, Location

def check_beverage_stock():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("CHECKING COCA COLA AND MINERAL WATER STOCK")
        print("=" * 70)
        
        # Find Coca Cola
        coca_cola = db.query(InventoryItem).filter(
            InventoryItem.name.ilike("%coca%cola%")
        ).first()
        
        if coca_cola:
            print(f"\n🥤 Coca Cola 750ml:")
            print(f"   ID: {coca_cola.id}")
            print(f"   Current Stock (Global): {coca_cola.current_stock}")
            print(f"   Min Stock Level: {coca_cola.min_stock_level}")
            print(f"   Unit Price: ₹{coca_cola.unit_price}")
            
            # Check location stocks
            location_stocks = db.query(LocationStock).filter(
                LocationStock.item_id == coca_cola.id
            ).all()
            
            if location_stocks:
                print(f"\n   Location Stocks:")
                for ls in location_stocks:
                    loc = db.query(Location).filter(Location.id == ls.location_id).first()
                    loc_name = f"{loc.building} - {loc.room_area}" if loc else f"Location {ls.location_id}"
                    print(f"     {loc_name}: {ls.quantity}")
            else:
                print(f"\n   ⚠️  No location stocks found!")
        else:
            print("\n❌ Coca Cola not found!")
        
        # Find Mineral Water
        mineral_water = db.query(InventoryItem).filter(
            InventoryItem.name.ilike("%mineral%water%")
        ).first()
        
        if mineral_water:
            print(f"\n💧 Mineral Water 1L:")
            print(f"   ID: {mineral_water.id}")
            print(f"   Current Stock (Global): {mineral_water.current_stock}")
            print(f"   Min Stock Level: {mineral_water.min_stock_level}")
            print(f"   Unit Price: ₹{mineral_water.unit_price}")
            
            # Check location stocks
            location_stocks = db.query(LocationStock).filter(
                LocationStock.item_id == mineral_water.id
            ).all()
            
            if location_stocks:
                print(f"\n   Location Stocks:")
                for ls in location_stocks:
                    loc = db.query(Location).filter(Location.id == ls.location_id).first()
                    loc_name = f"{loc.building} - {loc.room_area}" if loc else f"Location {ls.location_id}"
                    print(f"     {loc_name}: {ls.quantity}")
            else:
                print(f"\n   ⚠️  No location stocks found!")
        else:
            print("\n❌ Mineral Water not found!")
        
        print("\n" + "=" * 70)
        print("RECOMMENDATION")
        print("=" * 70)
        print("\nIf stock is 0, you need to:")
        print("1. Create a Purchase Order for these items")
        print("2. OR manually add stock via 'Add New Item' with initial stock")
        print("3. OR run the restore_beverage_stock.py script again")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_beverage_stock()
