"""
Check purchased history for Coca Cola and Mineral Water
"""
from app.database import SessionLocal
from app.models.inventory import InventoryItem, PurchaseDetail, PurchaseMaster
from sqlalchemy import func

def check_purchased_stock():
    db = SessionLocal()
    try:
        print("="*60)
        print("PURCHASE HISTORY CHECK")
        print("="*60)
        
        items_to_check = ["Coca Cola 750ml", "Mineral Water 1L"]
        
        for name in items_to_check:
            # Find the item first
            item = db.query(InventoryItem).filter(InventoryItem.name.ilike(f"%{name}%")).first()
            
            if item:
                print(f"\nItem: {item.name} (ID: {item.id})")
                
                # Query purchase details for this item
                purchase_details = db.query(PurchaseDetail).filter(
                    PurchaseDetail.item_id == item.id
                ).all()
                
                if purchase_details:
                    total_purchased = 0
                    print(f"  Found {len(purchase_details)} purchase records:")
                    
                    for detail in purchase_details:
                        # Get the master record to show date and vendor
                        purchase_master = db.query(PurchaseMaster).filter(
                            PurchaseMaster.id == detail.purchase_master_id
                        ).first()
                        
                        date_str = purchase_master.purchase_date if purchase_master else "Unknown Date"
                        vendor_name = purchase_master.vendor.name if (purchase_master and purchase_master.vendor) else "Unknown Vendor"
                        
                        print(f"    - Date: {date_str}, Qty: {detail.quantity}, Vendor: {vendor_name}")
                        total_purchased += detail.quantity
                        
                    print(f"  TOTAL PURCHASED: {total_purchased}")
                else:
                    print("  No purchase history found (0 purchased).")
            else:
                print(f"\nItem '{name}' not found in inventory master list.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_purchased_stock()
