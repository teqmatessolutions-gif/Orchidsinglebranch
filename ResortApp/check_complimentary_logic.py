import os
import sys
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
print(f"Loaded .env from: {env_path}")

# Add the ResortApp directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.inventory import InventoryItem, StockIssue, StockIssueDetail
from app.models.room import Room

db = SessionLocal()

print("\n=== Checking Complimentary Limit Configuration ===\n")

# Check Ice Cream
ice_cream = db.query(InventoryItem).filter(InventoryItem.name.ilike("%ice cream%")).first()
if ice_cream:
    print(f"Ice Cream (ID: {ice_cream.id})")
    print(f"  Complimentary Limit: {ice_cream.complimentary_limit}")
    print(f"  Selling Price: {ice_cream.selling_price}")
    print(f"  Is Sellable to Guest: {ice_cream.is_sellable_to_guest}")
    
# Check Coca Cola
coca_cola = db.query(InventoryItem).filter(InventoryItem.name.ilike("%coca cola%")).first()
if coca_cola:
    print(f"\nCoca Cola (ID: {coca_cola.id})")
    print(f"  Complimentary Limit: {coca_cola.complimentary_limit}")
    print(f"  Selling Price: {coca_cola.selling_price}")
    print(f"  Is Sellable to Guest: {coca_cola.is_sellable_to_guest}")

# Check Room 102 allocations
print("\n=== Checking Room 102 Stock Issues ===\n")
room_102 = db.query(Room).filter(Room.number == "102 (LUXURY)").first()
if room_102 and room_102.inventory_location_id:
    issues = db.query(StockIssue).filter(
        StockIssue.destination_location_id == room_102.inventory_location_id
    ).all()
    
    for issue in issues:
        print(f"Issue ID: {issue.id}, Date: {issue.issue_date}")
        for detail in issue.details:
            print(f"  - {detail.item.name if detail.item else 'Unknown'}")
            print(f"    Qty: {detail.issued_quantity}")
            print(f"    Is Payable: {detail.is_payable}")
            print(f"    Unit Price: {detail.unit_price}")
            print(f"    Rental Price: {detail.rental_price}")

db.close()
