
from app.utils.auth import get_db
from app.models.inventory import StockIssue, StockIssueDetail
from app.models.room import Room
from sqlalchemy.orm import joinedload

# Manually setup DB since I cannot import app.db.session directly due to path issues or whatever
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:qwerty123@localhost:5432/orchid_resort" # Hardcoded based on previous output
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

print("Checking recent Stock Issues...")
issues = db.query(StockIssue).order_by(StockIssue.created_at.desc()).limit(5).all()
for issue in issues:
    print(f"Issue {issue.issue_number}: Loc {issue.destination_location_id} Date {issue.issue_date}")
    for d in issue.details:
        print(f"  - Item {d.item_id}: Qty {d.issued_quantity}")

print("\nChecking Rooms with Inventory Locations...")
rooms = db.query(Room).filter(Room.inventory_location_id != None).all()
room_map = {}
for r in rooms:
    print(f"Room {r.number}: Location ID {r.inventory_location_id}")
    room_map[str(r.number)] = r

print("\nChecking Room 101...")
if "101" in room_map:
    room = room_map["101"]
    issues = db.query(StockIssue).filter(StockIssue.destination_location_id == room.inventory_location_id).all()
    print(f"Found {len(issues)} issues for Room 101 (Loc {room.inventory_location_id})")
else:
    print("Room 101 not found/synced")

print("\nChecking Room 102...")
if "102" in room_map:
    room = room_map["102"]
    issues = db.query(StockIssue).filter(StockIssue.destination_location_id == room.inventory_location_id).all()
    print(f"Found {len(issues)} issues for Room 102 (Loc {room.inventory_location_id})")
else:
    print("Room 102 not found/synced")
