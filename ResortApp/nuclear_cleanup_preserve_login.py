"""
NUCLEAR CLEANUP SCRIPT - PRESERVES LOGIN ONLY
Clears GLOBAL DATA (Master + Transactional) while preserving Admin Login.
Use with EXTREME CAUTION.
"""
from app.database import SessionLocal
from sqlalchemy import text
from app.models.user import User

def nuclear_cleanup():
    db = SessionLocal()
    
    def safe_delete(table_name):
        try:
            db.execute(text(f"DELETE FROM {table_name}"))
            db.commit()
            print(f"   ✅ {table_name} cleared")
        except Exception as e:
            db.rollback()
            # Ignore "does not exist" errors
            if "does not exist" in str(e) or "UndefinedTable" in str(e):
                pass
            else:
                print(f"   ⚠️  Could not clear {table_name}: {e}")

    try:
        print("=" * 70)
        print("☢️  NUCLEAR SYSTEM RESET - EXCEPT LOGIN")
        print("=" * 70)
        print("This will delete ALL data including:")
        print("  ❌ Master Data (Items, Rooms, Locations, Services, etc.)")
        print("  ❌ Transactional Data (Bookings, Purchases, etc.)")
        print("  ❌ Employee Records")
        print("ONLY the 'admin@teqmates.com' user will be preserved.")
        print("=" * 70)
        
        # Verify admin exists first
        admin = db.query(User).filter(User.email == "admin@teqmates.com").first()
        if not admin:
            print("❌ Admin user 'admin@teqmates.com' not found! Aborting to prevent lockout.")
            return

        response = input("Type 'DELETE EVERYTHING' to confirm: ")
        if response != "DELETE EVERYTHING":
            print("❌ Cancelled.")
            return

        print("\nStarting Nuclear Cleanup...")
        
        # 1. Transactional & Link Tables (Child tables)
        tables = [
             # Checkouts & Payments
            "checkout_verifications", "checkout_payments", "checkouts", "checkout_requests",
            
            # Inventory Transactions
            "inventory_transactions", "stock_issue_details", "stock_issues",
            "stock_requisition_details", "stock_requisitions", "purchase_details", "purchase_masters",
            "waste_logs", "location_stocks", "asset_mappings", "asset_registry",
            
            # Services & Food
            "employee_inventory_assignments", "assigned_services", "service_requests",
            "food_order_items", "food_orders", 
            
            # Bookings
            "booking_rooms", "package_booking_rooms", "package_bookings", "bookings",
            
             # Accounting
            "journal_entry_lines", "journal_entries", "accounts", "expenses", "payments",
            
            # Other
            "notifications", "working_logs", "attendances", "leaves", "suggestions"
        ]
        
        for t in tables:
            safe_delete(t)
            
        # 2. Master Data (Parent tables)
        # Order matters!
        
        # Inventory Master
        safe_delete("service_inventory_items")
        safe_delete("recipes") 
        safe_delete("recipe_ingredients")
        safe_delete("inventory_items")
        safe_delete("food_items")
        safe_delete("inventory_categories")
        safe_delete("food_categories")
        safe_delete("vendors")
        
        # Hotel Master
        safe_delete("package_images")
        safe_delete("packages")
        safe_delete("service_images")
        safe_delete("services")
        
        # Locations & Rooms
        # Note: Rooms often link to Locations. Locations link to Parent Locations.
        # We might need multiple passes or CASCADE.
        # Try clearing Locations first (if room depends on location? usually location depends on room or vice versa)
        # Checking models: Room has inventory_location_id. Location has parent_location_id.
        # So Room -> Location. Location -> Location.
        # Delete Room first IF Room depends on Location. 
        # Actually Room usually has 'room_type_id' etc.
        # Let's try deleting Rooms first, setting location_id to null if needed?
        # Or just delete.
        safe_delete("rooms")
        safe_delete("locations") 
        
        # Users & Employees
        # Delete all employees (they link to users)
        safe_delete("employees")
        
        # Delete all users EXCEPT admin
        print(f"   ℹ️  Cleaning users (preserving Admin ID {admin.id})...")
        try:
            db.execute(text(f"DELETE FROM users WHERE id != {admin.id}"))
            db.commit()
            print("   ✅ Users cleared (Admin preserved)")
        except Exception as e:
            db.rollback()
            print(f"   ❌ Error clearing users: {e}")
            
        print("\n" + "=" * 70)
        print("✅ NUCLEAR RESET COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    nuclear_cleanup()
