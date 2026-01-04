"""
COMPREHENSIVE DATA CLEANUP SCRIPT - ROBUST VERSION
Clears ALL transactional data while preserving master data.
Handles missing tables gracefully.
"""
from app.database import SessionLocal
from sqlalchemy import text

def clear_all_transactional_data():
    db = SessionLocal()
    
    def safe_delete(table_name):
        try:
            db.execute(text(f"DELETE FROM {table_name}"))
            db.commit() # Commit immediately to isolate this operation
            print(f"   ✅ {table_name} cleared")
        except Exception as e:
            db.rollback() # Rollback this specific failure so we can continue
            err = str(e).lower()
            if "does not exist" in err or "undefinedtable" in err:
                print(f"   ⚠️  {table_name} does not exist (skipping)")
            else:
                print(f"   ❌ Error clearing {table_name}: {e}")

    try:
        print("=" * 70)
        print("⚠️  COMPREHENSIVE DATA CLEANUP (ROBUST)")
        print("=" * 70)
        
        response = input("Are you SURE you want to proceed? (type 'YES' to confirm): ")
        
        if response != "YES":
            print("\n❌ Cleanup cancelled.")
            return
        
        print("\n" + "=" * 70)
        print("STARTING CLEANUP...")
        print("=" * 70)
        
        # 1. Clear Checkout-related data
        print("\n1. Clearing checkout data...")
        safe_delete("checkout_verifications")
        safe_delete("checkout_payments")
        safe_delete("checkouts")
        safe_delete("checkout_requests")
        
        # 2. Clear Service Requests
        print("\n2. Clearing service requests...")
        safe_delete("service_requests")
        
        # 3. Clear Food Orders
        print("\n3. Clearing food orders...")
        safe_delete("food_order_items")
        safe_delete("food_orders")
        
        # 4. Clear Assigned Services
        print("\n4. Clearing assigned services...")
        safe_delete("employee_inventory_assignments")
        safe_delete("assigned_services")
        
        # 5. Clear Bookings
        print("\n5. Clearing bookings...")
        safe_delete("booking_rooms")
        safe_delete("package_booking_rooms")
        safe_delete("package_bookings")
        safe_delete("bookings")
        
        # 6. Clear Asset Registry & Mappings
        print("\n6. Clearing asset registry & mappings...")
        safe_delete("asset_registry")
        safe_delete("asset_mappings")
        
        # 7. Clear Waste Logs
        print("\n7. Clearing waste logs...")
        safe_delete("waste_logs")
        
        # 8. Clear Stock Issues
        print("\n8. Clearing stock issues...")
        safe_delete("stock_issue_details")
        safe_delete("stock_issues")
        
        # 9. Clear Stock Requisitions
        print("\n9. Clearing stock requisitions...")
        safe_delete("stock_requisition_details")
        safe_delete("stock_requisitions")
        
        # 10. Clear Inventory Transactions FIRST (before purchases)
        print("\n10. Clearing inventory transactions...")
        safe_delete("inventory_transactions")
        
        # 11. Clear Purchases (after transactions)
        print("\n11. Clearing purchases...")
        safe_delete("purchase_details")
        safe_delete("purchase_masters")
        
        # 12. Clear Location Stocks
        print("\n12. Clearing location stocks...")
        safe_delete("location_stocks")
        
        # 13. Reset Inventory Item Stocks to 0
        print("\n13. Resetting inventory item stocks to 0...")
        try:
            db.execute(text("UPDATE inventory_items SET current_stock = 0"))
            db.commit()
            print("   ✅ Inventory stocks reset to 0")
        except Exception as e:
             db.rollback()
             print(f"   ❌ Error resetting stocks: {e}")

        
        # 14. Clear Accounting/Journal Entries(be careful with order if linked)
        print("\n14. Clearing accounting entries...")
        safe_delete("journal_entry_lines")
        # journal_entries might be linked to other things, tried deleting last?
        # But if we deleted purchases/transactions, it should be fine.
        safe_delete("journal_entries")
        
        # 15. Clear Notifications
        print("\n15. Clearing notifications...")
        safe_delete("notifications")
        
        # 16. Clear Expenses
        print("\n16. Clearing expenses...")
        safe_delete("expenses")
        
        # 17. Clear Attendance & Working Logs
        print("\n17. Clearing attendance & working logs...")
        safe_delete("working_logs")
        safe_delete("attendances")
        safe_delete("leaves")
        
        # Final status
        print("\n" + "=" * 70)
        print("✅ CLEANUP COMPLETE!")
        print("=" * 70)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_transactional_data()
