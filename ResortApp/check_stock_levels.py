from app.database import SessionLocal
from app.models.inventory import InventoryItem

db = SessionLocal()
try:
    # Check the stock levels for the items that were transferred
    items = db.query(InventoryItem).filter(
        InventoryItem.id.in_([3, 7, 11])  # Tomatoes, Milk, Chicken
    ).all()
    
    print("Current Stock Levels:")
    print("-" * 60)
    for item in items:
        print(f"ID: {item.id}")
        print(f"Name: {item.name}")
        print(f"Current Stock: {item.current_stock} {item.unit}")
        print("-" * 60)
        
finally:
    db.close()
