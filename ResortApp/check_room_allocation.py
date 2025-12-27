from app.database import SessionLocal
from app.models.inventory import StockIssue, StockIssueDetail, LocationStock
from app.models.room import Room
from sqlalchemy import desc

db = SessionLocal()

print("=== CHECKING ROOM ALLOCATION DATA ===\n")

# Find the latest checked-in booking
room = db.query(Room).filter(Room.number == "102").first()
if not room:
    print("Room 102 not found")
else:
    print(f"Room 102 Location ID: {room.inventory_location_id}")
    
    # Get stock issues for this room
    issues = db.query(StockIssue).filter(
        StockIssue.destination_location_id == room.inventory_location_id
    ).order_by(desc(StockIssue.id)).all()
    
    print(f"\nStock Issues to Room 102:")
    for issue in issues:
        print(f"\n  Issue #{issue.issue_number}:")
        for detail in issue.details:
            item_name = detail.item.name if detail.item else "Unknown"
            print(f"    - {item_name}: {detail.issued_quantity} pcs, is_payable={detail.is_payable}, notes={detail.notes}")
    
    # Get location stock
    stocks = db.query(LocationStock).filter(
        LocationStock.location_id == room.inventory_location_id
    ).all()
    
    print(f"\nCurrent Location Stock:")
    for stock in stocks:
        item_name = stock.item.name if stock.item else "Unknown"
        print(f"  - {item_name}: {stock.quantity} pcs")

db.close()
