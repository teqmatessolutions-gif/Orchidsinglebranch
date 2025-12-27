
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(r"c:\releasing\orchid\ResortApp")

try:
    from app.database import Base, get_db, SessionLocal
    from app.models.inventory import InventoryItem, LocationStock, Location, AssetMapping, AssetRegistry
except ImportError as e:
    print(f"Import Error: {e}")
    sys.path.append(r"c:\releasing\orchid")
    from ResortApp.app.database import Base, get_db, SessionLocal
    from ResortApp.app.models.inventory import InventoryItem, LocationStock, Location, AssetMapping, AssetRegistry

# Database setup
# DATABASE_URL = "postgresql://postgres:postgres@localhost/resort_db"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def verify_stock_counts():
    print("\n--- Stock Integrity Check ---\n")
    
    # 1. Get all Inventory Items and their Global Stock
    items = db.query(InventoryItem).all()
    global_stock_map = {item.id: float(item.current_stock or 0) for item in items}
    item_names = {item.id: item.name for item in items}
    
    total_global_stock = sum(global_stock_map.values())
    print(f"Total Global Stock (from InventoryItems): {total_global_stock}")
    
    # 2. Get all Location Stocks and sum them up
    location_stocks = db.query(LocationStock).all()
    loc_stock_map = {} # item_id -> quantity sum
    
    print("\n--- Location Stock Details ---")
    location_totals = {} # loc_id -> total count
    
    for ls in location_stocks:
        qty = float(ls.quantity or 0)
        # Only count positive stock for the sum (since users see positive stock)
        # But for integrity, we should count everything.
        if qty > 0:
            loc_stock_map[ls.item_id] = loc_stock_map.get(ls.item_id, 0) + qty
            
            # Track per location for validating the UI table
            location_totals[ls.location_id] = location_totals.get(ls.location_id, 0) + qty

    # 3. Mappings (Fixed Assets in Rooms often don't have LocationStock entries but exist)
    # My previous fix ENSURED that if LocationStock exists (even 0), we use it.
    # But if LocationStock does NOT exist, we might count AssetMapping?
    # Let's check if there are mapped assets that are NOT in LocationStock (or have 0 LocationStock but are mapped?)
    # Wait, simple logic: The UI Table sums `get_stock_by_location`.
    # Let's mimic `get_stock_by_location` logic roughly.
    
    # We'll just look for Mismatches first.
    
    total_loc_stock = sum(loc_stock_map.values())
    print(f"Total Location Stock (Sum of LocationStock > 0): {total_loc_stock}")
    
    print("\n--- Item Discrepancies (Global vs Location Sum) ---")
    print(f"{'Item Name':<30} | {'Global':<10} | {'Loc Sum':<10} | {'Diff':<10}")
    print("-" * 70)
    
    has_discrepancy = False
    for item_id, global_qty in global_stock_map.items():
        loc_qty = loc_stock_map.get(item_id, 0)
        if abs(global_qty - loc_qty) > 0.01:
            has_discrepancy = True
            diff = global_qty - loc_qty
            print(f"{item_names.get(item_id, 'Unknown'):<30} | {global_qty:<10} | {loc_qty:<10} | {diff:<10}")
            
    if not has_discrepancy:
        print("No discrepancies found between Global Stock and Location Stock sums!")
    
    print("\n--- Location Totals (Compare with UI) ---")
    locations = db.query(Location).all()
    for loc in locations:
        # Calculate exactly like the API does
        # 1. LocationStock
        l_stocks = db.query(LocationStock).filter(LocationStock.location_id == loc.id).all()
        seen = set()
        total_items = 0
        
        # Helper to mimic API logic
        items_map = {}
        for s in l_stocks:
            seen.add(s.item_id)
            if s.quantity > 0:
                items_map[s.item_id] = s.quantity
        
        # 2. AssetMapping
        mappings = db.query(AssetMapping).filter(AssetMapping.location_id == loc.id).all()
        for m in mappings:
            if m.item_id not in seen:
                 items_map[m.item_id] = items_map.get(m.item_id, 0) + m.quantity
        
        # Sum
        count = sum(items_map.values())
        if count > 0:
            print(f"Location: {loc.name:<30} | Calculated Count: {count}")

if __name__ == "__main__":
    verify_stock_counts()
