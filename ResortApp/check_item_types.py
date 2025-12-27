from app.database import SessionLocal
from app.models.inventory import InventoryItem, InventoryCategory

db = SessionLocal()

def list_item_types():
    print("--- Current Item Types ---")
    items = db.query(InventoryItem).all()
    
    print(f"{'ID':<5} | {'Name':<30} | {'Category':<20} | {'Type':<10}")
    print("-" * 75)
    
    for item in items:
        cat_name = item.category.name if item.category else "None"
        item_type = "Asset" if item.is_asset_fixed else "Consumable"
        print(f"{item.id:<5} | {item.name:<30} | {cat_name:<20} | {item_type:<10}")

    print("-" * 75)

if __name__ == "__main__":
    list_item_types()
