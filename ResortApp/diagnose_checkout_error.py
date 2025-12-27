import sys
import traceback
from app.database import SessionLocal
from app.models.checkout import CheckoutRequest as CheckoutRequestModel
from app.models.inventory import InventoryItem, LocationStock, StockIssue, StockIssueDetail
from app.models.room import Room

db = SessionLocal()

try:
    # Get the checkout request
    checkout_request = db.query(CheckoutRequestModel).filter(CheckoutRequestModel.id == 38).first()
    
    if not checkout_request:
        print("Checkout request 38 not found")
        sys.exit(1)
    
    print(f"Checkout Request ID: {checkout_request.id}")
    print(f"Room Number: {checkout_request.room_number}")
    print(f"Status: {checkout_request.status}")
    print(f"Inventory Data: {checkout_request.inventory_data}")
    
    # Get room
    room = db.query(Room).filter(Room.number == checkout_request.room_number).first()
    if room:
        print(f"\nRoom Location ID: {room.inventory_location_id}")
        
        # Get room stock
        if room.inventory_location_id:
            stocks = db.query(LocationStock).filter(
                LocationStock.location_id == room.inventory_location_id
            ).all()
            print(f"\nRoom Stock:")
            for s in stocks:
                print(f"  - {s.item.name if s.item else 'Unknown'}: {s.quantity}")
    
    print("\n=== Simulating Checkout Logic ===")
    
    # Simulate the logic
    if checkout_request.inventory_data:
        for item_data in checkout_request.inventory_data:
            print(f"\nProcessing item: {item_data}")
            
            item_id = item_data.get('item_id')
            if not item_id:
                print("  No item_id, skipping")
                continue
                
            inv_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
            if not inv_item:
                print(f"  Item {item_id} not found")
                continue
                
            print(f"  Item: {inv_item.name}")
            print(f"  Is Asset Fixed: {getattr(inv_item, 'is_asset_fixed', False)}")
            
            if not getattr(inv_item, 'is_asset_fixed', False):
                room_stock = db.query(LocationStock).filter(
                    LocationStock.location_id == room.inventory_location_id,
                    LocationStock.item_id == item_id
                ).first()
                
                allocated = room_stock.quantity if room_stock else 0.0
                used = item_data.get('used_qty', 0) or 0.0
                missing = item_data.get('missing_qty', 0) or 0.0
                unused = allocated - used - missing
                
                print(f"  Allocated: {allocated}, Used: {used}, Missing: {missing}, Unused: {unused}")
                
                if unused > 0:
                    # Find source
                    last_issue = db.query(StockIssue).join(StockIssueDetail).filter(
                        StockIssue.destination_location_id == room.inventory_location_id,
                        StockIssueDetail.item_id == item_id
                    ).order_by(StockIssue.id.desc()).first()
                    
                    if last_issue:
                        print(f"  Source Location ID: {last_issue.source_location_id}")
                    else:
                        print("  No stock issue found for this item!")

except Exception as e:
    print(f"\n\nERROR: {e}")
    traceback.print_exc()
finally:
    db.close()
