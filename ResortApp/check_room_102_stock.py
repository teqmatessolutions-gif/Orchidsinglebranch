from app.database import SessionLocal
from app.models.inventory import StockIssue, StockIssueDetail, InventoryItem

db = SessionLocal()

# Find Location 19 (Room 102 - from previous step)
location_id = 19

print(f"Checking Stock Issues for Location ID: {location_id}")

issues = db.query(StockIssue).filter(StockIssue.destination_location_id == location_id).all()

count = 0
for issue in issues:
    for detail in issue.details:
        item = db.query(InventoryItem).get(detail.item_id)
        if item:
            print(f"  Item: {item.name}, Qty: {detail.issued_quantity}, Payable: {detail.is_payable}")
            print(f"        Fixed Asset? {item.is_asset_fixed}, Laundry? {item.track_laundry_cycle}")
            print(f"        Sellable? {item.is_sellable_to_guest}, Perishable? {item.is_perishable}")
            count += 1

if count == 0:
    print("No items found allocated to this room.")

db.close()
