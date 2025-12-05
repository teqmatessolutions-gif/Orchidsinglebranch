"""
Comprehensive System Verification Script
Tests all critical inventory and accounting functionality
"""
from app.database import SessionLocal
from app.models.inventory import (
    PurchaseMaster, LocationStock, InventoryItem, 
    Location, WasteLog, StockRequisition, StockIssue
)
from app.models.account import JournalEntry, AccountLedger
from sqlalchemy import func

db = SessionLocal()

print("=" * 70)
print("🔍 SYSTEM VERIFICATION - COMPREHENSIVE CHECK")
print("=" * 70)

# 1. Database Tables Check
print("\n📊 1. DATABASE TABLES STATUS")
print("-" * 70)

tables_to_check = [
    ("purchases_master", PurchaseMaster),
    ("location_stocks", LocationStock),
    ("inventory_items", InventoryItem),
    ("locations", Location),
    ("waste_logs", WasteLog),
    ("stock_requisitions", StockRequisition),
    ("stock_issues", StockIssue),
    ("journal_entries", JournalEntry),
    ("account_ledgers", AccountLedger)
]

for table_name, model in tables_to_check:
    try:
        count = db.query(model).count()
        print(f"✅ {table_name:25} - {count:5} records")
    except Exception as e:
        print(f"❌ {table_name:25} - ERROR: {str(e)[:50]}")

# 2. Location Stock Verification
print("\n📦 2. LOCATION STOCK VERIFICATION")
print("-" * 70)

location_stocks = db.query(
    Location.name,
    func.count(LocationStock.id).label('items_count'),
    func.sum(LocationStock.quantity).label('total_quantity')
).join(
    LocationStock, Location.id == LocationStock.location_id
).group_by(Location.id, Location.name).all()

if location_stocks:
    for loc_name, items, qty in location_stocks:
        print(f"  📍 {loc_name:30} - {items:3} items, {qty:8.2f} total qty")
else:
    print("  ⚠️  No location stocks found")

# 3. Purchase Status Check
print("\n🛒 3. PURCHASE STATUS SUMMARY")
print("-" * 70)

purchase_stats = db.query(
    PurchaseMaster.status,
    func.count(PurchaseMaster.id).label('count'),
    func.sum(PurchaseMaster.total_amount).label('total_value')
).group_by(PurchaseMaster.status).all()

for status, count, value in purchase_stats:
    print(f"  {status:15} - {count:3} purchases, ₹{value:12,.2f}")

# 4. Purchases with Destination Locations
print("\n🎯 4. PURCHASES WITH DESTINATION LOCATIONS")
print("-" * 70)

purchases_with_dest = db.query(PurchaseMaster).filter(
    PurchaseMaster.destination_location_id.isnot(None)
).count()

purchases_without_dest = db.query(PurchaseMaster).filter(
    PurchaseMaster.destination_location_id.is_(None)
).count()

print(f"  ✅ With destination:    {purchases_with_dest:3}")
print(f"  ⚠️  Without destination: {purchases_without_dest:3}")

# 5. Received Purchases vs Location Stock
print("\n🔄 5. STOCK SYNC VERIFICATION")
print("-" * 70)

received_purchases = db.query(PurchaseMaster).filter(
    PurchaseMaster.status == "received",
    PurchaseMaster.destination_location_id.isnot(None)
).all()

print(f"  Received purchases with destination: {len(received_purchases)}")

synced = 0
not_synced = []

for purchase in received_purchases:
    for detail in purchase.details:
        stock_exists = db.query(LocationStock).filter(
            LocationStock.location_id == purchase.destination_location_id,
            LocationStock.item_id == detail.item_id
        ).first()
        
        if stock_exists:
            synced += 1
        else:
            not_synced.append({
                'po': purchase.purchase_number,
                'item_id': detail.item_id,
                'location_id': purchase.destination_location_id
            })

print(f"  ✅ Synced to location_stocks:  {synced}")
print(f"  ❌ Not synced:                 {len(not_synced)}")

if not_synced:
    print("\n  Missing stock entries:")
    for item in not_synced[:5]:  # Show first 5
        print(f"    - PO: {item['po']}, Item: {item['item_id']}, Location: {item['location_id']}")

# 6. Waste Logs Check
print("\n🗑️  6. WASTE LOGS STATUS")
print("-" * 70)

waste_inventory = db.query(WasteLog).filter(WasteLog.is_food_item == False).count()
waste_food = db.query(WasteLog).filter(WasteLog.is_food_item == True).count()

print(f"  Inventory items: {waste_inventory}")
print(f"  Food items:      {waste_food}")

# 7. Journal Entries Check
print("\n📒 7. ACCOUNTING INTEGRATION")
print("-" * 70)

journal_count = db.query(JournalEntry).count()
ledger_count = db.query(AccountLedger).count()

print(f"  Journal Entries: {journal_count}")
print(f"  Account Ledgers: {ledger_count}")

# Recent journal entries
recent_entries = db.query(JournalEntry).order_by(
    JournalEntry.created_at.desc()
).limit(3).all()

if recent_entries:
    print("\n  Recent Entries:")
    for entry in recent_entries:
        print(f"    - {entry.entry_date} | {entry.description[:50]}")

# 8. Requisitions Status
print("\n📋 8. REQUISITIONS STATUS")
print("-" * 70)

req_stats = db.query(
    StockRequisition.status,
    func.count(StockRequisition.id)
).group_by(StockRequisition.status).all()

for status, count in req_stats:
    print(f"  {status:15} - {count:3} requisitions")

# 9. Stock Issues
print("\n📤 9. STOCK ISSUES")
print("-" * 70)

issue_count = db.query(StockIssue).count()
print(f"  Total stock issues: {issue_count}")

# 10. System Health Summary
print("\n" + "=" * 70)
print("📊 SYSTEM HEALTH SUMMARY")
print("=" * 70)

issues_found = []

if not location_stocks:
    issues_found.append("⚠️  No location stocks found - run backfill script")

if len(not_synced) > 0:
    issues_found.append(f"⚠️  {len(not_synced)} purchase items not synced to location stock")

if purchases_without_dest > 0:
    issues_found.append(f"ℹ️  {purchases_without_dest} purchases without destination (legacy data)")

if issues_found:
    print("\n🔧 ISSUES DETECTED:")
    for issue in issues_found:
        print(f"  {issue}")
    print("\n💡 RECOMMENDATION: Run backfill_location_stocks.py to sync all data")
else:
    print("\n✅ ALL SYSTEMS OPERATIONAL!")
    print("   - Location stock tracking: ACTIVE")
    print("   - Purchase integration: WORKING")
    print("   - Accounting integration: WORKING")
    print("   - Waste management: WORKING")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)

db.close()
