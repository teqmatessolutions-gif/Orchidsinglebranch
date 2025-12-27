
from app.database import SessionLocal
from app.models.inventory import PurchaseMaster, PurchaseDetail, InventoryItem, InventoryCategory
from sqlalchemy import func

def debug_facility_capital_investment():
    db = SessionLocal()
    dept = "Facility"
    print(f"--- Debugging Capital Investment for {dept} ---")
    
    try:
        # Get all purchase details for this department
        details = db.query(PurchaseDetail, PurchaseMaster, InventoryItem).join(
            PurchaseMaster, PurchaseDetail.purchase_master_id == PurchaseMaster.id
        ).join(
            InventoryItem, PurchaseDetail.item_id == InventoryItem.id
        ).join(
            InventoryCategory, InventoryItem.category_id == InventoryCategory.id
        ).filter(
            InventoryCategory.parent_department == dept
        ).all()
        
        total_sum = 0
        print(f"{'Date':<12} | {'PO Number':<15} | {'Item Name':<30} | {'Qty':<5} | {'Unit Price':<10} | {'Total':<10}")
        print("-" * 90)
        
        for detail, master, item in details:
            print(f"{str(master.purchase_date):<12} | {master.purchase_number:<15} | {item.name:<30} | {detail.quantity:<5} | {detail.unit_price:<10} | {detail.total_amount:<10}")
            total_sum += detail.total_amount
            
        print("-" * 90)
        print(f"Total Capital Investment Calculated: {total_sum}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_facility_capital_investment()
