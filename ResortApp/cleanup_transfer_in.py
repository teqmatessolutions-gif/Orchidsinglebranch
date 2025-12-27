#!/usr/bin/env python3
"""
Clean up TRANSFER_IN transactions that are incorrectly affecting global stock calculation.
These transactions are for location tracking only and should not be counted in global stock.
"""

from app.database import SessionLocal
from app.models.inventory import InventoryTransaction

db = SessionLocal()

print("🧹 Cleaning up TRANSFER_IN transactions...")
print("=" * 60)

# Find all TRANSFER_IN transactions
transfer_in_txns = db.query(InventoryTransaction).filter(
    InventoryTransaction.transaction_type == "transfer_in"
).all()

print(f"\nFound {len(transfer_in_txns)} TRANSFER_IN transactions")

# Group by item
from collections import defaultdict
by_item = defaultdict(list)
for txn in transfer_in_txns:
    by_item[txn.item_id].append(txn)

print(f"Affecting {len(by_item)} different items\n")

delete_count = 0
for item_id, txns in by_item.items():
    item_name = txns[0].item.name if txns[0].item else f"Item #{item_id}"
    total_qty = sum(txn.quantity for txn in txns)
    
    print(f"📦 {item_name}: {len(txns)} transactions, total qty: {total_qty}")
    
    for txn in txns:
        db.delete(txn)
        delete_count += 1

print(f"\n{'=' * 60}")
print(f"🗑️  Deleted {delete_count} TRANSFER_IN transactions")
print("✅ Stock movements are tracked by Stock Issues and Location Stocks")

db.commit()
db.close()

print("\n✅ Cleanup complete! Transaction history should now match stock levels.")
