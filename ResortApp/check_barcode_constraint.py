from app.database import SessionLocal
from sqlalchemy import text, inspect
from app.models.inventory import InventoryItem

db = SessionLocal()

# Check barcode column constraints
result = db.execute(text("""
    SELECT 
        conname as constraint_name,
        contype as constraint_type
    FROM pg_constraint 
    WHERE conrelid = 'inventory_items'::regclass 
    AND conname LIKE '%barcode%'
"""))

print("Barcode constraints:")
for row in result:
    print(f"  {row[0]}: {row[1]}")

# Check if barcode has unique constraint
result2 = db.execute(text("""
    SELECT indexname, indexdef 
    FROM pg_indexes 
    WHERE tablename = 'inventory_items' 
    AND indexdef LIKE '%barcode%'
"""))

print("\nBarcode indexes:")
for row in result2:
    print(f"  {row[0]}: {row[1]}")

db.close()
