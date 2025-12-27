
from app.database import SessionLocal
from app.models.inventory import PurchaseMaster, PurchaseDetail, InventoryItem, InventoryCategory
from app.models.foodorder import FoodOrder
from sqlalchemy import func

def debug_restaurant_metrics():
    db = SessionLocal()
    dept = "Restaurant"
    print(f"--- Debugging Metrics for {dept} ---")
    
    try:
        # 1. Capital Investment
        print("\n[1] Capital Investment (Purchases)")
        details = db.query(PurchaseDetail, PurchaseMaster, InventoryItem).join(
            PurchaseMaster, PurchaseDetail.purchase_master_id == PurchaseMaster.id
        ).join(
            InventoryItem, PurchaseDetail.item_id == InventoryItem.id
        ).join(
            InventoryCategory, InventoryItem.category_id == InventoryCategory.id
        ).filter(
            InventoryCategory.parent_department == dept
        ).all()
        
        capital_investment = 0
        print(f"{'Date':<12} | {'Item':<30} | {'Qty':<5} | {'Price':<10} | {'Total':<10}")
        print("-" * 80)
        for detail, master, item in details:
            print(f"{str(master.purchase_date):<12} | {item.name[:30]:<30} | {detail.quantity:<5} | {detail.unit_price:<10} | {detail.total_amount:<10}")
            capital_investment += detail.total_amount
        print(f"Total Capital Investment: {capital_investment}")

        # 2. Assets
        print("\n[2] Assets (Fixed Assets + Items > 10,000)")
        # Fixed Assets
        fixed_assets = db.query(InventoryItem).join(InventoryCategory).filter(
            InventoryCategory.parent_department == dept,
            InventoryItem.is_asset_fixed == True,
            InventoryItem.current_stock > 0
        ).all()
        
        # High Value Items
        high_value = db.query(InventoryItem).join(InventoryCategory).filter(
            InventoryCategory.parent_department == dept,
            InventoryItem.is_asset_fixed == False,
            InventoryItem.unit_price >= 10000,
            InventoryItem.current_stock > 0
        ).all()
        
        assets_total = 0
        print(f"{'Item':<30} | {'Stock':<5} | {'Unit Price':<10} | {'Value':<10} | {'Type':<10}")
        print("-" * 80)
        for item in fixed_assets:
            val = item.current_stock * item.unit_price
            print(f"{item.name[:30]:<30} | {item.current_stock:<5} | {item.unit_price:<10} | {val:<10} | {'Fixed Asset'}")
            assets_total += val
            
        for item in high_value:
            val = item.current_stock * item.unit_price
            print(f"{item.name[:30]:<30} | {item.current_stock:<5} | {item.unit_price:<10} | {val:<10} | {'High Value'}")
            assets_total += val
            
        print(f"Total Assets Value: {assets_total}")

        # 3. Income
        print("\n[3] Income (Food Orders)")
        food_income = db.query(func.sum(FoodOrder.amount)).scalar() or 0
        print(f"Total Food Order Income: {food_income}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_restaurant_metrics()
