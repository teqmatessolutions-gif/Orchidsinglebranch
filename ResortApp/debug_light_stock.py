from app.database import SessionLocal
from app.models.inventory import InventoryItem, LocationStock, AssetMapping, WasteLog

db = SessionLocal()

def inspect_light_stats():
    print("--- Inspecting Item 'light' ---")
    
    # Get Item
    # Using ilike just in case, though we know it's "light"
    item = db.query(InventoryItem).filter(InventoryItem.name.ilike("light")).first()
    
    if not item:
        print("Item 'light' not found.")
        return

    print(f"Item ID: {item.id}")
    print(f"Global 'Current Stock' (item.current_stock): {item.current_stock}")
    
    # Get Warehouse Stock (Loc ID 1)
    wh_stock = db.query(LocationStock).filter(
        LocationStock.item_id == item.id, 
        LocationStock.location_id == 1
    ).first()
    wh_qty = wh_stock.quantity if wh_stock else 0
    print(f"Warehouse Stock (Loc 1): {wh_qty}")
    
    # Get Assigned Count (Asset Mappings)
    mappings = db.query(AssetMapping).filter(
        AssetMapping.item_id == item.id,
        AssetMapping.is_active == True
    ).all()
    assigned_qty = sum(m.quantity or 1 for m in mappings)
    print(f"Total Assigned (Active Mappings): {assigned_qty}")
    for m in mappings:
        print(f"  - Mapping {m.id}: Loc {m.location_id}, Qty {m.quantity}")

    # Get Waste Count
    waste_logs = db.query(WasteLog).filter(WasteLog.item_id == item.id).all()
    waste_qty = sum(w.quantity for w in waste_logs)
    print(f"Total Waste: {waste_qty}")
    
    # Expected Calculation
    # If Start = 70 (User said)
    # Expected Available (Warehouse) = Start - Waste - Assigned
    start = 70.0
    expected_wh = start - waste_qty - assigned_qty
    print(f"\n--- Calculation ---")
    print(f"Start (User claim): {start}")
    print(f" - Waste: {waste_qty}")
    print(f" - Assigned: {assigned_qty}")
    print(f" = Expected Warehouse/Stock: {expected_wh}")
    print(f" vs Actual Global Stock: {item.current_stock}")
    print(f" vs Actual Warehouse Stock: {wh_qty}")

if __name__ == "__main__":
    inspect_light_stats()
