#!/usr/bin/env python3
"""
Comprehensive Transactional Data Cleanup Script
Clears all transactional data while preserving master data.
"""

from app.database import SessionLocal
from sqlalchemy import text
import sys

def cleanup_all_transactions():
    db = SessionLocal()
    
    try:
        print("🧹 Starting comprehensive data cleanup...")
        print("=" * 70)
        
        # List of tables to clear (in order to respect foreign key constraints)
        cleanup_queries = [
            # Journal Entries (Accounting)
            ("DELETE FROM journal_entry_lines", "Journal Entry Lines"),
            ("DELETE FROM journal_entries", "Journal Entries"),
            
            # Checkouts and related
            ("DELETE FROM checkout_payments", "Checkout Payments"),
            ("DELETE FROM checkout_verifications", "Checkout Verifications"),
            ("UPDATE checkout_requests SET checkout_id = NULL", "Checkout Request Links"),
            ("DELETE FROM checkouts", "Checkouts"),
            ("DELETE FROM checkout_requests", "Checkout Requests"),
            
            # Service Requests (must be before food orders due to FK)
            ("DELETE FROM service_requests", "Service Requests"),
            
            # Service Assignments
            ("DELETE FROM assigned_services", "Assigned Services"),
            
            # Food Orders
            ("DELETE FROM food_order_items", "Food Order Items"),
            ("DELETE FROM food_orders", "Food Orders"),
            
            # Bookings
            ("DELETE FROM booking_rooms", "Booking Room Links"),
            ("DELETE FROM bookings", "Bookings"),
            
            # Package Bookings
            ("DELETE FROM package_booking_rooms", "Package Booking Room Links"),
            ("DELETE FROM package_bookings", "Package Bookings"),
            
            # Inventory Transactions
            ("DELETE FROM stock_issue_details", "Stock Issue Details"),
            ("DELETE FROM stock_issues", "Stock Issues"),
            ("DELETE FROM inventory_transactions", "Inventory Transactions"),
            ("DELETE FROM waste_logs", "Waste Logs"),
            
            # Asset Registry
            ("DELETE FROM asset_registry", "Asset Registry"),
            
            # Purchases
            ("DELETE FROM purchase_details", "Purchase Details"),
            ("DELETE FROM purchase_masters", "Purchase Masters"),
            
            # Reset Location Stock to Zero
            ("UPDATE location_stocks SET quantity = 0, last_updated = NOW()", "Location Stocks (Reset to 0)"),
            
            # Reset Room Status
            ("UPDATE rooms SET status = 'Available'", "Room Status (Reset to Available)"),
        ]
        
        total_deleted = 0
        
        for query, description in cleanup_queries:
            try:
                result = db.execute(text(query))
                rows_affected = result.rowcount if hasattr(result, 'rowcount') else 0
                print(f"✓ {description}: {rows_affected} records")
                total_deleted += rows_affected
            except Exception as e:
                print(f"✗ {description}: Error - {str(e)}")
                db.rollback()
                raise
        
        db.commit()
        
        print("=" * 70)
        print(f"✅ Cleanup complete! Total records affected: {total_deleted}")
        print("\n📋 Summary:")
        print("   - All transactional data cleared")
        print("   - All inventory stock reset to 0")
        print("   - All rooms set to Available")
        print("   - Master data preserved (items, categories, locations, users, etc.)")
        print("\n💡 Next steps:")
        print("   1. Create new purchases to add stock")
        print("   2. Create new bookings")
        print("   3. Test the system with fresh data")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    response = input("\n⚠️  WARNING: This will delete ALL transactional data!\nAre you sure? (yes/no): ")
    if response.lower() == 'yes':
        cleanup_all_transactions()
    else:
        print("❌ Cleanup cancelled.")
