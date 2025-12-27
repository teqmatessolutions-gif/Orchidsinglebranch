"""
COMPREHENSIVE DATA CLEANUP SCRIPT - FINAL CORRECTED VERSION
Clears ALL transactional data while preserving master data.
"""
from app.database import SessionLocal
from sqlalchemy import text

def clear_all_transactional_data():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("⚠️  COMPREHENSIVE DATA CLEANUP")
        print("=" * 70)
        print("\nThis will DELETE:")
        print("  ❌ All Bookings (regular & package)")
        print("  ❌ All Services (assigned)")
        print("  ❌ All Purchases")
        print("  ❌ All Stock Issues")
        print("  ❌ All Transactions")
        print("  ❌ All Waste Logs")
        print("  ❌ All Asset Mappings")
        print("  ❌ All Asset Registry")
        print("  ❌ All Location Stocks")
        print("  ❌ All Checkout Requests")
        print("  ❌ All Food Orders")
        print("  ❌ All Service Requests")
        print("  ❌ All Reports Data")
        print("\nThis will KEEP:")
        print("  ✅ Users/Login")
        print("  ✅ Inventory Items")
        print("  ✅ Categories")
        print("  ✅ Locations")
        print("  ✅ Vendors")
        print("  ✅ Employees")
        print("  ✅ Rooms")
        print("  ✅ Services (definitions)")
        
        print("\n" + "=" * 70)
        response = input("Are you SURE you want to proceed? (type 'YES' to confirm): ")
        
        if response != "YES":
            print("\n❌ Cleanup cancelled.")
            return
        
        print("\n" + "=" * 70)
        print("STARTING CLEANUP...")
        print("=" * 70)
        
        # Order matters due to foreign key constraints!
        # Delete child tables first, then parent tables
        
        # 1. Clear Checkout-related data
        print("\n1. Clearing checkout data...")
        db.execute(text("DELETE FROM checkout_verifications"))
        db.execute(text("DELETE FROM checkout_payments"))
        db.execute(text("DELETE FROM checkouts"))
        db.execute(text("DELETE FROM checkout_requests"))
        print("   ✅ Checkout data cleared")
        
        # 2. Clear Service Requests
        print("\n2. Clearing service requests...")
        db.execute(text("DELETE FROM service_requests"))
        print("   ✅ Service requests cleared")
        
        # 3. Clear Food Orders
        print("\n3. Clearing food orders...")
        db.execute(text("DELETE FROM food_order_items"))
        db.execute(text("DELETE FROM food_orders"))
        print("   ✅ Food orders cleared")
        
        # 4. Clear Assigned Services
        print("\n4. Clearing assigned services...")
        db.execute(text("DELETE FROM employee_inventory_assignments"))
        db.execute(text("DELETE FROM assigned_services"))
        print("   ✅ Assigned services cleared")
        
        # 5. Clear Bookings
        print("\n5. Clearing bookings...")
        db.execute(text("DELETE FROM booking_rooms"))
        db.execute(text("DELETE FROM package_booking_rooms"))
        db.execute(text("DELETE FROM package_bookings"))
        db.execute(text("DELETE FROM bookings"))
        print("   ✅ Bookings cleared")
        
        # 6. Clear Asset Registry & Mappings
        print("\n6. Clearing asset registry & mappings...")
        db.execute(text("DELETE FROM asset_registry"))
        db.execute(text("DELETE FROM asset_mappings"))
        print("   ✅ Asset data cleared")
        
        # 7. Clear Waste Logs
        print("\n7. Clearing waste logs...")
        db.execute(text("DELETE FROM waste_logs"))
        print("   ✅ Waste logs cleared")
        
        # 8. Clear Stock Issues
        print("\n8. Clearing stock issues...")
        db.execute(text("DELETE FROM stock_issue_details"))
        db.execute(text("DELETE FROM stock_issues"))
        print("   ✅ Stock issues cleared")
        
        # 9. Clear Stock Requisitions
        print("\n9. Clearing stock requisitions...")
        db.execute(text("DELETE FROM stock_requisition_details"))
        db.execute(text("DELETE FROM stock_requisitions"))
        print("   ✅ Stock requisitions cleared")
        
        # 10. Clear Inventory Transactions FIRST (before purchases)
        print("\n10. Clearing inventory transactions...")
        db.execute(text("DELETE FROM inventory_transactions"))
        print("   ✅ Inventory transactions cleared")
        
        # 11. Clear Purchases (after transactions)
        print("\n11. Clearing purchases...")
        db.execute(text("DELETE FROM purchase_details"))
        db.execute(text("DELETE FROM purchase_masters"))
        print("   ✅ Purchases cleared")
        
        # 12. Clear Location Stocks
        print("\n12. Clearing location stocks...")
        db.execute(text("DELETE FROM location_stocks"))
        print("   ✅ Location stocks cleared")
        
        # 13. Reset Inventory Item Stocks to 0
        print("\n13. Resetting inventory item stocks to 0...")
        db.execute(text("UPDATE inventory_items SET current_stock = 0"))
        print("   ✅ Inventory stocks reset to 0")
        
        # 14. Clear Accounting/Journal Entries
        print("\n14. Clearing accounting entries...")
        db.execute(text("DELETE FROM journal_entry_lines"))
        db.execute(text("DELETE FROM journal_entries"))
        print("   ✅ Accounting entries cleared")
        
        # 15. Clear Notifications
        print("\n15. Clearing notifications...")
        db.execute(text("DELETE FROM notifications"))
        print("   ✅ Notifications cleared")
        
        # 16. Clear Expenses
        print("\n16. Clearing expenses...")
        db.execute(text("DELETE FROM expenses"))
        print("   ✅ Expenses cleared")
        
        # 17. Clear Attendance & Working Logs
        print("\n17. Clearing attendance & working logs...")
        db.execute(text("DELETE FROM working_logs"))
        db.execute(text("DELETE FROM attendances"))
        db.execute(text("DELETE FROM leaves"))
        print("   ✅ Attendance data cleared")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "=" * 70)
        print("✅ CLEANUP COMPLETE!")
        print("=" * 70)
        print("\nThe system has been reset to a clean state.")
        print("You can now start fresh with new bookings, purchases, etc.")
        print("\n📊 Summary:")
        print("  • All transactional data has been deleted")
        print("  • Inventory items now have 0 stock")
        print("  • Master data (items, categories, locations, etc.) preserved")
        print("  • You'll need to create purchases to add stock")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_transactional_data()
