"""
Check LED Bulb category and fix if needed
"""
from app.database import SessionLocal
from app.models.inventory import InventoryItem, InventoryCategory

def check_led_bulb_category():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("CHECKING LED BULB CATEGORY")
        print("=" * 70)
        
        # Find LED Bulb
        led_bulb = db.query(InventoryItem).filter(
            InventoryItem.name.ilike("%LED Bulb%")
        ).first()
        
        if not led_bulb:
            print("\n❌ LED Bulb not found!")
            return
        
        print(f"\n✅ Found: {led_bulb.name}")
        print(f"   Category ID: {led_bulb.category_id}")
        
        # Get category
        if led_bulb.category_id:
            category = db.query(InventoryCategory).filter(
                InventoryCategory.id == led_bulb.category_id
            ).first()
            
            if category:
                print(f"\n📁 Category: {category.name}")
                print(f"   Is Fixed Asset: {category.is_asset_fixed}")
                print(f"   Is Consumable: {category.is_consumable}")
                
                if not category.is_asset_fixed:
                    print("\n⚠️  PROBLEM: Category is NOT marked as Fixed Asset!")
                    print("\nTo fix this:")
                    print("1. Go to Inventory → Categories")
                    print(f"2. Edit '{category.name}' category")
                    print("3. Check 'Is Fixed Asset' checkbox")
                    print("4. Save")
                    
                    # Or we can fix it here
                    print("\n" + "=" * 70)
                    print("WOULD YOU LIKE TO FIX THIS NOW?")
                    print("=" * 70)
                    print("\nUncomment the lines below in the script to auto-fix:")
                    print("# category.is_asset_fixed = True")
                    print("# db.commit()")
                    print("# print('✅ Fixed! Category is now marked as Fixed Asset')")
                else:
                    print("\n✅ Category is correctly marked as Fixed Asset")
            else:
                print("\n❌ Category not found!")
        else:
            print("\n❌ LED Bulb has no category assigned!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_led_bulb_category()
