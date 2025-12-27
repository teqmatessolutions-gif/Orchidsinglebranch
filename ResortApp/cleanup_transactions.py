#!/usr/bin/env python3
"""
Clean up incorrect TRANSFER_OUT transactions that were reducing global stock.
These transactions were created during stock issues (transfers between locations)
but should not have been counted against global stock.
"""

from app.database import SessionLocal
from app.models.inventory import InventoryTransaction
from datetime import datetime

db = SessionLocal()

print("🧹 Cleaning up incorrect TRANSFER_OUT transactions...")
print("=" * 60)

# Find all TRANSFER_OUT transactions
# These should only exist for location tracking, not global stock
transfer_out_txns = db.query(InventoryTransaction).filter(
    InventoryTransaction.transaction_type == "transfer_out"
).all()

print(f"\nFound {len(transfer_out_txns)} TRANSFER_OUT transactions")

# Group by item
from collections import defaultdict
by_item = defaultdict(list)
for txn in transfer_out_txns:
    by_item[txn.item_id].append(txn)

print(f"Affecting {len(by_item)} different items\n")

# Option 1: Delete all TRANSFER_OUT transactions (they're redundant)
# Option 2: Keep them but mark them differently
# Option 3: Convert them to a different type that doesn't affect stock calculation

# Let's go with Option 1: Delete them
# The stock movements are already tracked by:
# - Stock Issue records (StockIssue/StockIssueDetail)
# - Location Stock changes (LocationStock)
# - TRANSFER_IN transactions at destination

delete_count = 0
for item_id, txns in by_item.items():
    item_name = txns[0].item.name if txns[0].item else f"Item #{item_id}"
    total_qty = sum(txn.quantity for txn in txns)
    
    print(f"📦 {item_name}: {len(txns)} transactions, total qty: {total_qty}")
    
    for txn in txns:
        db.delete(txn)
        delete_count += 1

print(f"\n{'=' * 60}")
print(f"🗑️  Deleted {delete_count} TRANSFER_OUT transactions")
print("✅ These movements are still tracked by Stock Issues and Location Stocks")

db.commit()
db.close()

print("\n✅ Cleanup complete! Transaction history should now match stock levels.")
