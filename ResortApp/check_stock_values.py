"""
Check and display inventory stock values to identify the issue
"""
from app.database import SessionLocal
from app.models.inventory import InventoryItem


def check_stock_values():
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("INVENTORY STOCK VALUE ANALYSIS")
        print("=" * 80)
        print()
        
        items = db.query(InventoryItem).all()
        
        print(f"{'ITEM NAME':<30} {'STOCK':>10} {'UNIT':>8} {'UNIT PRICE':>12} {'TOTAL VALUE':>15}")
        print("=" * 80)
        
        total_value = 0.0
        
        for item in items:
            stock = item.current_stock or 0
            unit_price = item.unit_price or 0
            total = stock * unit_price
            total_value += total
            
            print(f"{item.name:<30} {stock:>10.2f} {item.unit:>8} ₹{unit_price:>11.2f} ₹{total:>14.2f}")
        
        print("=" * 80)
        print(f"{'TOTAL STOCK VALUE':>62} ₹{total_value:>14.2f}")
        print()
        
        # Check if any items have missing unit prices
        missing_price = [item for item in items if not item.unit_price or item.unit_price == 0]
        
        if missing_price:
            print()
            print("⚠️  Items with missing or zero unit price:")
            for item in missing_price:
                print(f"  - {item.name} (Stock: {item.current_stock} {item.unit})")
            print()
            print("These items are not contributing to the total stock value.")
            print("You should set unit prices for these items.")
        
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR")
        print("=" * 80)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    check_stock_values()
