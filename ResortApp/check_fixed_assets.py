import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.inventory import InventoryItem
from sqlalchemy.orm import joinedload

db = next(get_db())

# Query items with TV or Bulb in name
items = db.query(InventoryItem).options(joinedload(InventoryItem.category)).filter(
    (InventoryItem.name.ilike('%TV%')) | (InventoryItem.name.ilike('%Bulb%'))
).all()

print("\n" + "="*80)
print("CHECKING FIXED ASSET STATUS")
print("="*80 + "\n")

if not items:
    print("❌ No items found with 'TV' or 'Bulb' in name")
else:
    for item in items:
        is_fixed = getattr(item, 'is_asset_fixed', None)
        category_name = item.category.name if item.category else "No Category"
        
        print(f"Item: {item.name}")
        print(f"  - is_asset_fixed: {is_fixed}")
        print(f"  - Category: {category_name}")
        
        if is_fixed:
            print(f"  ✅ Marked as FIXED ASSET")
        else:
            print(f"  ❌ NOT marked as fixed asset")
        print()

print("="*80)
