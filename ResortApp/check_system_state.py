from app.database import SessionLocal
from app.models.inventory import InventoryItem, PurchaseMaster, StockIssue, LocationStock

db = SessionLocal()

print("=== SYSTEM STATE CHECK ===")

# 1. Global Stock
print("\n--- Global Inventory Stock ---")
items = db.query(InventoryItem).filter(InventoryItem.current_stock > 0).all()
if not items:
    print("ALL GLOBAL STOCK IS 0.")
else:
    for i in items:
        print(f"Item {i.name} (ID: {i.id}): Stock {i.current_stock}")

# 2. Purchases
print("\n--- Recent Purchases ---")
purchases = db.query(PurchaseMaster).all()
print(f"Total Purchases: {len(purchases)}")
for p in purchases:
    print(f"- PO: {p.purchase_number}, Status: {p.status}")

# 3. Stock Issues (Allocations)
print("\n--- Stock Issues (Allocations) ---")
issues = db.query(StockIssue).all()
print(f"Total Stock Issues: {len(issues)}")
for i in issues:
    print(f"- Issue: {i.issue_number}, Dest: {i.destination_location_id}")

db.close()
