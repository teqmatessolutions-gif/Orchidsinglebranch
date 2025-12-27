from app.database import SessionLocal
from app.models.inventory import StockIssue, StockIssueDetail, LocationStock, Location, InventoryItem
from sqlalchemy import desc

db = SessionLocal()

print("=== Debgging Recent Stock Issues ===")
# Get latest stock issue
latest_issue = db.query(StockIssue).order_by(desc(StockIssue.created_at)).first()
if latest_issue:
    print(f"Latest Issue ID: {latest_issue.id}, Number: {latest_issue.issue_number}")
    print(f"  Source Loc ID: {latest_issue.source_location_id}")
    print(f"  Dest Loc ID: {latest_issue.destination_location_id}")
    print(f"  Date: {latest_issue.issue_date}")
    
    if latest_issue.destination_location_id:
        dest_loc = db.query(Location).filter(Location.id == latest_issue.destination_location_id).first()
        print(f"  Destination Location: {dest_loc.name} (ID: {dest_loc.id}) Type: {dest_loc.location_type}")

    print("  Details:")
    for d in latest_issue.details:
        item = db.query(InventoryItem).get(d.item_id)
        print(f"    - Item: {item.name} (ID: {d.item_id})")
        print(f"      Issued Qty: {d.issued_quantity}")
        print(f"      Is Payable: {getattr(d, 'is_payable', 'N/A')}") 
        
        # Check Location Stock for this item at destination
        if latest_issue.destination_location_id:
            loc_stock = db.query(LocationStock).filter(
                LocationStock.location_id == latest_issue.destination_location_id,
                LocationStock.item_id == d.item_id
            ).first()
            if loc_stock:
                print(f"      -> Current Location Stock in DB: {loc_stock.quantity}")
            else:
                print(f"      -> NO Location Stock record found for Loc {latest_issue.destination_location_id} and Item {d.item_id}")

else:
    print("No Stock Issues found.")

print("\n=== Checking Room Locations ===")
rooms = db.query(Location).filter(Location.location_type == 'GUEST_ROOM').all()
for r in rooms:
    print(f"Room: {r.name} (Area: {r.room_area}) - ID: {r.id}")

db.close()
