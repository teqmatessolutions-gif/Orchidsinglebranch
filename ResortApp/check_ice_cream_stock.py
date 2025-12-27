import os
import sys
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Add the ResortApp directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.inventory import InventoryItem, LocationStock, StockIssue, StockIssueDetail
from app.models.room import Room

db = SessionLocal()

print("\n=== Checking Ice Cream Stock Levels ===\n")

# Find Ice Cream
ice_cream = db.query(InventoryItem).filter(InventoryItem.name.ilike("%ice cream%")).first()
if not ice_cream:
    print("Ice Cream not found")
    db.close()
    exit()

print(f"Ice Cream (ID: {ice_cream.id})")
print(f"  Name: {ice_cream.name}")
print(f"  Current Stock (Global): {ice_cream.current_stock}")

# Check location stocks
print(f"\n=== Location Stock for Ice Cream ===\n")
location_stocks = db.query(LocationStock).filter(LocationStock.item_id == ice_cream.id).all()

for ls in location_stocks:
    from app.models.inventory import Location
    location = db.query(Location).filter(Location.id == ls.location_id).first()
    print(f"Location: {location.name if location else 'Unknown'} (ID: {ls.location_id})")
    print(f"  Quantity: {ls.quantity}")
    print(f"  Last Updated: {ls.last_updated}")
    print()

# Check Room 103 specifically
print(f"=== Room 103 Stock ===\n")
room_103 = db.query(Room).filter(Room.number.ilike("%103%")).first()
if room_103 and room_103.inventory_location_id:
    room_stock = db.query(LocationStock).filter(
        LocationStock.location_id == room_103.inventory_location_id,
        LocationStock.item_id == ice_cream.id
    ).first()
    
    if room_stock:
        print(f"Room 103 Ice Cream Stock: {room_stock.quantity}")
    else:
        print("No ice cream stock record for Room 103")
    
    # Check stock issues
    print(f"\n=== Stock Issues for Room 103 (Ice Cream) ===\n")
    issues = db.query(StockIssue).filter(
        StockIssue.destination_location_id == room_103.inventory_location_id
    ).all()
    
    total_issued = 0
    for issue in issues:
        for detail in issue.details:
            if detail.item_id == ice_cream.id:
                print(f"Issue ID: {issue.id}, Date: {issue.issue_date}")
                print(f"  Quantity: {detail.issued_quantity}")
                print(f"  Is Payable: {detail.is_payable}")
                total_issued += detail.issued_quantity
    
    print(f"\nTotal Issued: {total_issued}")
    if room_stock:
        print(f"Current Stock: {room_stock.quantity}")
        print(f"Difference: {room_stock.quantity - total_issued}")

db.close()
