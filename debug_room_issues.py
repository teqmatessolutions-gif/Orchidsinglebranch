from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.inventory import StockIssue, StockIssueDetail, Location, InventoryItem

from app.database import SessionLocal, engine
# DATABASE_URL = "sqlite:///./resort.db"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def diagnose_issues(room_number="101"):
    print(f"--- Diagnosing Stock Issues for Room {room_number} ---")
    
    # 1. Find Room Location ID
    # Usually Room objects map to a Location, but here we check StockIssues by destination
    
    # Let's find the room first to get its inventory_location_id
    # Assuming standard setup where room number helps find it, but checkout.py looks up Room model
    from app.models.room import Room
    room = db.query(Room).filter(Room.number == room_number).first()
    
    if not room:
        print(f"Room {room_number} not found!")
        return
        
    loc_id = room.inventory_location_id
    print(f"Room Inventory Location ID: {loc_id}")
    
    if not loc_id:
        print("Room has no inventory location assigned.")
        return

    # 2. Query Stock Issues
    issues = (
        db.query(StockIssueDetail)
        .join(StockIssue, StockIssue.id == StockIssueDetail.issue_id)
        .join(InventoryItem, InventoryItem.id == StockIssueDetail.item_id)
        .filter(StockIssue.destination_location_id == loc_id)
        .all()
    )
    
    print(f"Found {len(issues)} Issue Details for this location.")
    
    print(f"{'Item Name':<20} | {'ID':<5} | {'Qty':<5} | {'RentPrice':<10} | {'IsPayable':<10} | {'Notes'}")
    print("-" * 80)
    
    for d in issues:
        item_name = d.item.name
        is_payable_db = getattr(d, 'is_payable', 'N/A')
        notes = d.notes or ""
        
        print(f"{item_name:<20} | {d.item_id:<5} | {d.issued_quantity:<5} | {str(d.rental_price):<10} | {str(is_payable_db):<10} | {notes}")

if __name__ == "__main__":
    diagnose_issues()
