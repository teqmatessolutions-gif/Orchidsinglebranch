from app.database import SessionLocal
from app.models.inventory import StockIssue, StockIssueDetail, LocationStock
from sqlalchemy import desc

db = SessionLocal()

print("=== CHECKING LATEST STOCK ISSUE ===\n")

# Get the most recent stock issue
latest_issue = db.query(StockIssue).order_by(desc(StockIssue.id)).first()

if not latest_issue:
    print("No stock issues found!")
else:
    print(f"Issue Number: {latest_issue.issue_number}")
    print(f"Source Location ID: {latest_issue.source_location_id}")
    print(f"Destination Location ID: {latest_issue.destination_location_id}")
    print(f"Issue Date: {latest_issue.issue_date}")
    print(f"\nDetails:")
    
    for detail in latest_issue.details:
        print(f"  - Item ID: {detail.item_id}, Quantity: {detail.issued_quantity}")
        print(f"    Item Name: {detail.item.name if detail.item else 'Unknown'}")

print("\n=== CHECKING LOCATION STOCKS ===\n")

# Check all location stocks
stocks = db.query(LocationStock).all()
for stock in stocks:
    loc_name = stock.location.name if stock.location else f"Location {stock.location_id}"
    item_name = stock.item.name if stock.item else f"Item {stock.item_id}"
    print(f"{loc_name}: {item_name} = {stock.quantity}")

db.close()
