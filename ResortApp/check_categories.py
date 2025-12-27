from app.database import SessionLocal
from app.models.inventory import InventoryCategory

db = SessionLocal()

def list_categories():
    print("--- Categories and their Defaults ---")
    cats = db.query(InventoryCategory).all()
    
    print(f"{'ID':<5} | {'Name':<30} | {'Is Asset Fixed':<10}")
    print("-" * 60)
    for c in cats:
        print(f"{c.id:<5} | {c.name:<30} | {c.is_asset_fixed:<10}")

if __name__ == "__main__":
    list_categories()
