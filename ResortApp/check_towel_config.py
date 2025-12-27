from app.database import SessionLocal
from app.models.inventory import StockIssue, StockIssueDetail, InventoryItem, Location

db = SessionLocal()

# 1. Find Kitchen Hand Towel
towel = db.query(InventoryItem).filter(InventoryItem.name.ilike("%Kitchen Hand Towel%")).first()
if not towel:
    print("Kitchen Hand Towel not found!")
else:
    print(f"Item: {towel.name} (ID: {towel.id})")
    print(f"  Is Fixed Asset: {towel.is_asset_fixed}")
    print(f"  Track Laundry: {towel.track_laundry_cycle}")
    print(f"  Is Sellable to Guest: {towel.is_sellable_to_guest}")
    print(f"  Is Perishable: {towel.is_perishable}")

# 2. Check Allocation in Room 102 (Location 19)
location_id = 19
print(f"\nChecking Allocations for Location {location_id}...")

issues = db.query(StockIssue).filter(StockIssue.destination_location_id == location_id).all()
found = False
for issue in issues:
    for detail in issue.details:
        if detail.item_id == towel.id:
            print(f"  FOUND ALLOCATION!")
            print(f"  Issue ID: {issue.id}, Qty: {detail.issued_quantity}")
            print(f"  Unit Price (Recorded): {detail.unit_price}")
            found = True

if not found:
    print("  No allocation found for Kitchen Hand Towel in Room 102.")

db.close()
