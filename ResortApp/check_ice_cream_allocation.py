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

print("\n=== Checking Ice Cream Allocations ===\n")

# Find Room 103
room_103 = db.query(Room).filter(Room.number.ilike("%103%")).first()
if not room_103:
    print("Room 103 not found")
    db.close()
    exit()

print(f"Room: {room_103.number}")
print(f"Location ID: {room_103.inventory_location_id}")

# Find Ice Cream
ice_cream = db.query(InventoryItem).filter(InventoryItem.name.ilike("%ice cream%")).first()
if not ice_cream:
    print("Ice Cream not found")
    db.close()
    exit()

print(f"\nIce Cream (ID: {ice_cream.id})")
print(f"  Complimentary Limit: {ice_cream.complimentary_limit}")
print(f"  Selling Price: {ice_cream.selling_price}")

# Check stock issues for this room
print(f"\n=== Stock Issues for Room 103 ===\n")
issues = db.query(StockIssue).filter(
    StockIssue.destination_location_id == room_103.inventory_location_id
).all()

ice_cream_complimentary = 0
ice_cream_payable = 0

for issue in issues:
    for detail in issue.details:
        if detail.item_id == ice_cream.id:
            print(f"Issue ID: {issue.id}, Date: {issue.issue_date}")
            print(f"  Item: {detail.item.name}")
            print(f"  Quantity: {detail.issued_quantity}")
            print(f"  Is Payable: {detail.is_payable}")
            print(f"  Unit Price: {detail.unit_price}")
            print()
            
            if detail.is_payable:
                ice_cream_payable += detail.issued_quantity
            else:
                ice_cream_complimentary += detail.issued_quantity

print(f"=== Summary ===")
print(f"Total Ice Cream Complimentary: {ice_cream_complimentary}")
print(f"Total Ice Cream Payable: {ice_cream_payable}")
print(f"Total Ice Cream: {ice_cream_complimentary + ice_cream_payable}")

db.close()
