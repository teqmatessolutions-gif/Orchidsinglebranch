from app.database import SessionLocal
from app.models.inventory import StockIssue, StockIssueDetail, InventoryItem, Location
from app.models.room import Room
from sqlalchemy.orm import joinedload
from sqlalchemy import desc

def check_return_loc(room_no, item_name):
    db = SessionLocal()
    try:
        # 1. Get Room Location
        room = db.query(Room).filter(Room.number == room_no).first()
        if not room:
            print(f"Room {room_no} not found")
            return
        loc_id = room.inventory_location_id
        print(f"Room {room_no} Location ID: {loc_id}")

        # 2. Get Item ID
        item = db.query(InventoryItem).filter(InventoryItem.name.ilike(f"%{item_name}%")).first()
        if not item:
            print(f"Item {item_name} not found")
            return
        print(f"Item: {item.name} (ID: {item.id})")

        # 3. Find latest StockIssue for this item to this room
        # We need the issue that put it there to know where it came from.
        # Check StockIssue joined with Detail
        last_issue = (db.query(StockIssue)
                      .join(StockIssueDetail)
                      .filter(StockIssue.destination_location_id == loc_id,
                              StockIssueDetail.item_id == item.id)
                      .order_by(desc(StockIssue.issue_date))
                      .first())

        if last_issue:
            source = db.query(Location).get(last_issue.source_location_id)
            print(f"\n--- RETURN PREDICTION ---")
            print(f"Original Issue: {last_issue.issue_number} on {last_issue.issue_date}")
            print(f"Source Location ID: {last_issue.source_location_id}")
            print(f"Source Location Name: {source.name if source else 'Unknown'}")
            print(f"Type: {source.location_type if source else 'Unknown'}")
            print(f"-------------------------")
            print(f"Logic used: The system prioritizes returning items to their 'Original Source Location'.")
        else:
            print("No previous Stock Issue found. System will try to find a warehouse with existing stock.")

    finally:
        db.close()

if __name__ == "__main__":
    check_return_loc("101", "LED Bulb")
