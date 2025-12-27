from app.database import SessionLocal
from app.models.inventory import StockIssue, Location

def check_issue_source(issue_id):
    db = SessionLocal()
    try:
        issue = db.query(StockIssue).filter(StockIssue.id == issue_id).first()
        if not issue:
            print(f"Issue {issue_id} not found")
        else:
            print(f"Issue {issue_id} Source Location ID: {issue.source_location_id}")
            loc = db.query(Location).filter(Location.id == issue.source_location_id).first()
            if loc:
                print(f"Source Location Name: {loc.name}")
                print(f"Type: {loc.location_type}")
            else:
                print("Source Location Not Found")
    finally:
        db.close()

if __name__ == "__main__":
    check_issue_source(241)
