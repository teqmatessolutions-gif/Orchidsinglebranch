"""
Check current stock of Coca Cola and Mineral Water
"""
from app.database import SessionLocal
from app.models.inventory import InventoryItem

def check_stock():
    db = SessionLocal()
    try:
        print("="*60)
        print("CURRENT STOCK LEVEL CHECK")
        print("="*60)
        
        items_to_check = ["Coca Cola 750ml", "Mineral Water 1L"]
        
        for name in items_to_check:
            item = db.query(InventoryItem).filter(InventoryItem.name.ilike(f"%{name}%")).first()
            if item:
                print(f"Item: {item.name}")
                print(f"Current Stock: {item.current_stock}")
                print(f"Status: {'In Stock' if item.current_stock > 0 else 'Out of Stock'}")
                print("-" * 30)
            else:
                print(f"Item {name} not found!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_stock()
