# Check-In Inventory Assignment Issue

## Problem Statement

When a guest checks in to a room:
- **Both Coca Cola AND Mineral Water** are assigned to the room
- **Only Mineral Water** is deducted from inventory stock
- **Coca Cola** remains at 40 pcs (not deducted)

**Expected Behavior:**
- Both items should be deducted from inventory when assigned at check-in

**Actual Behavior:**
- Only some items are deducted, others are not

## Possible Root Causes

### Cause 1: Partial Transaction Failure

The check-in process might be:
1. Assigning both items to the room ✅
2. Attempting to deduct inventory for both items
3. **Failing silently** for Coca Cola (maybe due to an error)
4. Successfully deducting Water ✅

**Why this might happen:**
- Database constraint violation for Coca Cola
- Missing location stock for Coca Cola
- Transaction error that's being caught and ignored

### Cause 2: Different Deduction Logic

The system might have two different code paths:
1. **Path A**: Assigns items to room + deducts stock (Water uses this)
2. **Path B**: Assigns items to room WITHOUT deducting stock (Coca Cola uses this)

**Why this might happen:**
- Items from different categories handled differently
- Items from different locations handled differently
- Complimentary vs. paid items handled differently

### Cause 3: Location Stock Issue

When assigning inventory at check-in:
- System tries to deduct from a specific location (e.g., "Main Kitchen Store")
- **Water exists** in that location → Deducted ✅
- **Coca Cola doesn't exist** in that location → Skipped ❌

**Why this might happen:**
- Items are in different storage locations
- Location stock not properly initialized for Coca Cola
- Missing LocationStock record for Coca Cola

### Cause 4: Item Category/Type Difference

The items might be treated differently based on their properties:
- **Water**: Category = "Beverages", Department = "Facility"
- **Coca Cola**: Category = "Electrical & Electronics", Department = "Facility"

If Coca Cola is miscategorized, it might be skipped during deduction.

## Investigation Steps

### Step 1: Check Backend Logs

Look for check-in related logs:
```
[DEBUG] Assigning inventory items to room...
[DEBUG] Deducted X pcs of Mineral Water
[WARNING] Failed to deduct Coca Cola: <error message>
```

### Step 2: Check Transaction History

1. Go to **Inventory → Transactions**
2. Filter by **Item = Mineral Water**
3. Look for "out" transaction at check-in time
4. Filter by **Item = Coca Cola**
5. Check if there's a corresponding "out" transaction

**Expected:**
- Both items should have "out" transactions at the same timestamp

**If Coca Cola has no transaction:**
- The deduction logic is failing or skipping it

### Step 3: Check Location Stock

1. Go to **Inventory → Location Stock**
2. Check which locations have **Mineral Water**
3. Check which locations have **Coca Cola**

**If Coca Cola is missing from the location:**
- That's why it wasn't deducted

### Step 4: Check Item Categories

1. Go to **Inventory → Items**
2. Click on **Mineral Water** → Check category/department
3. Click on **Coca Cola** → Check category/department

**If categories are different:**
- The check-in logic might only deduct items from specific categories

### Step 5: Check Room Allocation Data

The system might store which items are "allocated" to a room separately from inventory deduction.

Check if there's a table like:
- `room_inventory_allocations`
- `booking_inventory_items`
- `room_consumables`

## Temporary Workaround

### Manual Deduction Script

Create a script to manually deduct Coca Cola:

```python
from app.database import SessionLocal
from app.models.inventory import InventoryItem, InventoryTransaction
from datetime import datetime

db = SessionLocal()

# Find Coca Cola
coca_cola = db.query(InventoryItem).filter(
    InventoryItem.name.ilike("%Coca Cola%")
).first()

if coca_cola:
    # Deduct 1 unit (or however many were assigned)
    quantity_to_deduct = 1
    
    coca_cola.current_stock -= quantity_to_deduct
    
    # Create transaction
    transaction = InventoryTransaction(
        item_id=coca_cola.id,
        transaction_type="out",
        quantity=quantity_to_deduct,
        unit_price=coca_cola.unit_price,
        total_amount=coca_cola.unit_price * quantity_to_deduct if coca_cola.unit_price else None,
        reference_number="MANUAL-CHECKIN-DEDUCTION",
        notes="Manual deduction for check-in (Room 102)",
        created_by=None
    )
    db.add(transaction)
    db.commit()
    
    print(f"✅ Deducted {quantity_to_deduct} {coca_cola.unit} of {coca_cola.name}")
    print(f"   New stock: {coca_cola.current_stock}")
else:
    print("❌ Coca Cola not found")

db.close()
```

## Recommended Fix

### Option 1: Fix Check-In Logic

Find the check-in inventory assignment code and ensure:
1. All assigned items are deducted from stock
2. Errors are logged (not silently ignored)
3. Location stock is properly updated

### Option 2: Add Validation

Add a check after check-in to verify:
```python
# After assigning items to room
assigned_items = get_room_assigned_items(room_id)
for item in assigned_items:
    # Verify transaction exists
    transaction = db.query(InventoryTransaction).filter(
        InventoryTransaction.item_id == item.id,
        InventoryTransaction.reference_number.like(f"%CHECKIN%{room_number}%")
    ).first()
    
    if not transaction:
        print(f"[ERROR] No transaction found for {item.name} - creating now")
        # Create the missing transaction
        ...
```

### Option 3: Audit and Reconcile

Create a daily reconciliation script:
1. Check all rooms with active bookings
2. Get list of items assigned to each room
3. Verify corresponding inventory transactions exist
4. Flag discrepancies for manual review

## Questions to Answer

1. **Where is the check-in inventory assignment code?**
   - Which file/function handles this?
   - Is it in `booking.py`, `room.py`, or elsewhere?

2. **How are items assigned to rooms?**
   - Via services?
   - Via a separate room allocation system?
   - Via booking extras?

3. **Are there any error logs?**
   - Check backend console output
   - Check database logs
   - Check application logs

4. **Is this consistent?**
   - Does it happen for all check-ins?
   - Only for specific items?
   - Only for specific rooms/bookings?

## Next Steps

1. **Check backend logs** during next check-in
2. **Monitor transaction creation** in real-time
3. **Identify the exact code** that handles check-in inventory
4. **Add debug logging** to trace the issue
5. **Fix the root cause** once identified

## Summary

**Issue:** Items assigned at check-in are not all being deducted from inventory stock

**Impact:** Inventory counts are incorrect, leading to:
- Inaccurate stock levels
- Potential stockouts not detected
- Incorrect COGS calculations
- Audit discrepancies

**Priority:** HIGH - This affects inventory accuracy and financial reporting

**Status:** 🔴 Investigation needed - Requires code review to identify check-in inventory logic
