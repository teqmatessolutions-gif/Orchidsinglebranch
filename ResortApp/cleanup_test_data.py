"""
Simple Cleanup Script - Clear ALL transactional data using SQL
This is faster and doesn't require importing all models
"""

from app.database import SessionLocal
from sqlalchemy import text

def clear_all_transactional_data():
    """Clear all transactional data using direct SQL"""
    
    db = SessionLocal()
    try:
        print("🧹 Starting comprehensive data cleanup...")
        
        # Disable foreign key checks temporarily
        db.execute(text("SET session_replication_role = 'replica';"))
        
        tables_to_clear = [
            # Checkout & Billing
            ("checkout_requests", "Checkout Requests"),
            ("checkouts", "Completed Checkouts"),
            ("billings", "Billings"),
            
            # Waste & Services
            ("waste_logs", "Waste Logs"),
            ("service_request_assignments", "Service Assignments"),
            ("service_requests", "Service Requests"),
            ("food_orders", "Food Orders"),
            
            # Bookings
            ("booking_rooms", "Booking Rooms"),
            ("bookings", "Bookings"),
            ("package_booking_rooms", "Package Booking Rooms"),
            ("package_bookings", "Package Bookings"),
            
            # Inventory Transactions & Stock
            ("stock_requisition_details", "Stock Requisition Details"),
            ("stock_requisitions", "Stock Requisitions"),
            ("stock_issue_details", "Stock Issue Details"),
            ("stock_issues", "Stock Issues"),
            ("inventory_transactions", "Inventory Transactions"),
            ("location_stocks", "Location Stock"),  # Fixed table name
            
            # Purchases
            ("purchase_details", "Purchase Details"),
            ("purchase_masters", "Purchase Masters"),
            
            # Asset Management
            ("asset_mappings", "Asset Mappings"),
            ("asset_registry", "Asset Registry"),
            
            # Financial/Payments/Expenses
            ("payments", "Payments"),
            ("expenses", "Expenses"),
        ]
        
        cleared_count = 0
        skipped_count = 0
        
        for table_name, display_name in tables_to_clear:
            try:
                result = db.execute(text(f"DELETE FROM {table_name}"))
                rows = result.rowcount
                if rows > 0:
                    print(f"   ✓ Cleared {display_name}: {rows} rows deleted")
                    cleared_count += 1
                else:
                    print(f"   - {display_name}: already empty")
                    cleared_count += 1
                db.commit() # Commit after each table to persist changes even if next one fails
            except Exception as e:
                print(f"   ⚠ Failed to clear {display_name}: {e}")
                skipped_count += 1
                # Don't fail, just continue
                db.rollback()
                db.execute(text("SET session_replication_role = 'replica';"))  # Re-disable FK checks
        
        # Reset all inventory stock levels to 0
        print("   ➤ Resetting all inventory stock to 0...")
        result = db.execute(text("UPDATE inventory_items SET current_stock = 0"))
        print(f"   ✓ Reset stock for {result.rowcount} items to 0")
        
        # Re-enable foreign key checks
        db.execute(text("SET session_replication_role = 'origin';"))
        
        db.commit()
        print("\n✅ COMPLETE DATA CLEANUP - ALL TRANSACTIONS & STOCK CLEARED!")
        print("\n📊 Summary:")
        print(f"   - Tables cleared: {cleared_count}")
        print(f"   - Tables skipped: {skipped_count}")
        print("   - All inventory stock levels reset to 0")
        print("   - Purchases, bookings, services, assets, location stock - ALL CLEARED")
        print("   - Master data preserved (items, categories, vendors, locations, rooms)")
        print("   - Ready for completely fresh testing!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during cleanup: {e}")
        # Try to re-enable foreign keys even if error occurred
        try:
            db.execute(text("SET session_replication_role = 'origin';"))
            db.commit()
        except:
            pass
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_transactional_data()
