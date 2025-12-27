from app.database import SessionLocal
from app.models.inventory import InventoryItem, StockIssue, StockIssueDetail
from sqlalchemy.orm import joinedload

def test_query():
    db = SessionLocal()
    try:
        # Pick a location that likely has issues
        # Or just run the query without filter to check syntax
        print("Testing query syntax...")
        
        # We need a location ID to filter, let's just use 1 for testing syntax
        location_id = 1
        
        all_issue_details = (
            db.query(StockIssueDetail)
            .join(StockIssue, StockIssue.id == StockIssueDetail.issue_id)
            .join(InventoryItem, InventoryItem.id == StockIssueDetail.item_id)
            .options(joinedload(StockIssueDetail.item).joinedload(InventoryItem.category))
            .filter(StockIssue.destination_location_id == location_id)
            .all()
        )
        print(f"Query successful. Found {len(all_issue_details)} details.")
        
        for detail in all_issue_details:
            item = detail.item
            if item:
                print(f"Item: {item.name}, Category: {item.category.name if item.category else 'None'}")
                break
                
    except Exception as e:
        print(f"Query FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
