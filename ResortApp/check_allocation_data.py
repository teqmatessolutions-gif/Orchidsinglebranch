from app.database import SessionLocal
from app.models.inventory import StockIssue, StockIssueDetail, LocationStock
from app.models.room import Room
from sqlalchemy import or_

db = SessionLocal()

# Find the latest checked-in room
room = db.query(Room).filter(Room.status == "Checked-in").order_by(Room.id.desc()).first()
if not room:
    # Just get any room with inventory
    room = db.query(Room).filter(Room.inventory_location_id.isnot(None)).order_by(Room.id.desc()).first()

if room:
    print(f"Room: {room.number} (ID: {room.id})")
    print(f"Location ID: {room.inventory_location_id}")
    
    # Get stock issues
    issues = db.query(StockIssue).filter(
        StockIssue.destination_location_id == room.inventory_location_id
    ).all()
    
    print(f"\nStock Issues to this room:")
    for issue in issues:
        print(f"\n  Issue #{issue.issue_number}:")
        for detail in issue.details:
            print(f"    Item: {detail.item.name if detail.item else 'Unknown'}")
            print(f"    Quantity: {detail.issued_quantity}")
            print(f"    is_payable: {detail.is_payable}")
            print(f"    Notes: {detail.notes}")
    
    # Get location stock
    stocks = db.query(LocationStock).filter(
        LocationStock.location_id == room.inventory_location_id
    ).all()
    
    print(f"\nCurrent Location Stock:")
    for stock in stocks:
        print(f"  {stock.item.name if stock.item else 'Unknown'}: {stock.quantity}")
else:
    print("No room found")

db.close()
