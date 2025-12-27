"""
Cleanup Script - Clear Transactional Data for Testing
Preserves master data (items, categories, vendors, locations, rooms, etc.)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "ResortApp"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.booking import Booking, BookingRoom
from app.models.Package import PackageBooking, PackageBookingRoom
from app.models.checkout import CheckoutRequest, Checkout, CheckoutVerification, CheckoutPayment
from app.models.inventory import (
    WasteLog, InventoryTransaction, LocationStock, 
    StockIssue, StockIssueDetail, AssetRegistry,
    StockRequisition, StockRequisitionDetail,
    PurchaseMaster, PurchaseDetail, InventoryItem, AssetMapping
)
from app.models.foodorder import FoodOrder, FoodOrderItem
from app.models.service_request import ServiceRequest
from app.models.service import AssignedService
from app.models.room import Room
from app.models.employee_inventory import EmployeeInventoryAssignment

def clear_transactional_data(db: Session):
    """Clear all transactional data while preserving master data"""
    
    try:
        print("🧹 Starting data cleanup...")
        
        # 1. Clear Checkout & Payments
        print("   ➤ Clearing checkouts & payments...")
        db.query(CheckoutPayment).delete()
        db.query(CheckoutVerification).delete()
        db.query(Checkout).delete()
        db.query(CheckoutRequest).delete()
        
        # 2. Clear Waste Logs
        print("   ➤ Clearing waste logs...")
        db.query(WasteLog).delete()
        
        # 3. Clear Service Requests & Assignments
        print("   ➤ Clearing service requests...")
        db.query(EmployeeInventoryAssignment).delete()
        db.query(AssignedService).delete()
        db.query(ServiceRequest).delete()
        
        # 4. Clear Food Orders
        print("   ➤ Clearing food orders...")
        db.query(FoodOrderItem).delete()
        db.query(FoodOrder).delete()
        
        # 5. Clear Billing Records (Virtual concept in this system, mostly Checkouts)
        # Note: Billing model was not found, assuming Checkout covers it.
        
        # 6. Clear Bookings
        print("   ➤ Clearing bookings...")
        db.query(BookingRoom).delete()
        db.query(Booking).delete()
        db.query(PackageBookingRoom).delete()
        db.query(PackageBooking).delete()
        
        # 7. Clear Stock Issues (Must be deleted before Requisitions due to FK)
        print("   ➤ Clearing stock issues...")
        db.query(StockIssueDetail).delete()
        db.query(StockIssue).delete()

        # 8. Clear Stock Requisitions
        print("   ➤ Clearing stock requisitions...")
        db.query(StockRequisitionDetail).delete()
        db.query(StockRequisition).delete()
        
        # 9. Clear Inventory Transactions
        print("   ➤ Clearing inventory transactions...")
        db.query(InventoryTransaction).delete()
        
        # 10. Clear Location Stock
        print("   ➤ Clearing location stock...")
        db.query(LocationStock).delete()
        
        # 11. Reset Asset Registry (clear damaged status, reset to active)
        print("   ➤ Resetting asset registry status...")
        assets = db.query(AssetRegistry).all()
        for asset in assets:
            asset.status = "active"
            asset.notes = None
        
        # 12. Clear Purchases
        print("   ➤ Clearing purchases...")
        db.query(PurchaseDetail).delete()
        db.query(PurchaseMaster).delete()

        # 13. Clear Asset Mappings
        print("   ➤ Clearing asset mappings...")
        db.query(AssetMapping).delete()
        
        # 14. Reset Inventory Item Cached Stock
        print("   ➤ Resetting inventory item cached stock...")
        items = db.query(InventoryItem).all()
        for item in items:
            item.current_stock = 0.0
        
        # 15. Reset Room Status
        print("   ➤ Resetting room status...")
        rooms = db.query(Room).all()
        for room in rooms:
            room.status = "Available"

        db.commit()
        print("✅ Data cleanup completed successfully!")
        print("\n📊 Summary:")
        print("   - All transactional data cleared (Checkouts, Bookings, Services, Food, Inventory)")
        print("   - Master data preserved")
        print("   - Asset registry status reset to 'active'")
        print("   - Ready for fresh testing!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during cleanup: {e}")
        raise

if __name__ == "__main__":
    db = SessionLocal()
    try:
        clear_transactional_data(db)
    finally:
        db.close()
