"""
Verification script - Check if tables are actually empty
"""
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("🔍 Verifying database cleanup...\n")
    
    tables_to_check = [
        "checkout_requests",
        "checkouts",
        "waste_logs",
        "service_requests",
        "food_orders",
        "bookings",
        "booking_rooms",
        "stock_issues",
        "stock_issue_details",
        "inventory_transactions",
        "location_stocks",
        "purchase_masters",
        "purchase_details",
        "asset_mappings",
        "asset_registry",
        "payments",
        "expenses",
    ]
    
    for table in tables_to_check:
        try:
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            status = "✅ EMPTY" if count == 0 else f"❌ HAS {count} ROWS"
            print(f"   {table:30s} {status}")
        except Exception as e:
            print(f"   {table:30s} ⚠️  Table doesn't exist or error")
    
    print("\n📦 Checking inventory stock levels...")
    result = db.execute(text("SELECT COUNT(*) FROM inventory_items WHERE current_stock > 0"))
    items_with_stock = result.scalar()
    if items_with_stock == 0:
        print("   ✅ All inventory items have 0 stock")
    else:
        print(f"   ❌ {items_with_stock} items still have stock > 0")
        
finally:
    db.close()
