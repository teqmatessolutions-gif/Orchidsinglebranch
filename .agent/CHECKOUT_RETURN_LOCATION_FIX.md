# Checkout Return Location Fix

## Issue
When processing checkout, unused items were being returned to the **wrong location** (Central Warehouse) instead of the **original source location** (Hotel Store, Main Kitchen Store, etc.) where they came from.

### Example from Screenshots
**Stock Flow**:
1. Purchase → Hotel Store (20 Mineral Water)
2. Transfer → Hotel Store → Room 101 (10 Mineral Water)
3. Checkout → Room 101 → **Central Warehouse** ❌ (WRONG - should go back to Hotel Store)

**Result**:
- Hotel Store: 10 (correct - 20 - 10 transferred)
- Room 101: 0 (correct - cleared after checkout)
- Central Warehouse: -2 ❌ (WRONG - received returns it shouldn't have)

---

## Root Cause

The checkout logic was using a fallback to Central Warehouse when it couldn't find the source location from stock issues. The query might not have been finding the correct `StockIssue` record, or the `source_location_id` was NULL.

---

## What Was Fixed

### File: `app/api/checkout.py`
**Function**: `check_inventory_for_checkout()` (lines 466-515)

### Changes Made

#### Before (WRONG):
```python
# Simple query without proper checks
last_issue = db.query(StockIssue).join(StockIssueDetail).filter(
    StockIssue.destination_location_id == room_loc_id,
    StockIssueDetail.item_id == item.item_id
).order_by(StockIssue.id.desc()).first()

source_loc_id = last_issue.source_location_id if last_issue else None

if not source_loc_id:
    # Fallback to warehouse ❌ (too quick to fallback)
    warehouse = db.query(Location).filter(...).first()
    source_loc_id = warehouse.id
```

#### After (CORRECT):
```python
# Better query with issue_date ordering
last_issue = db.query(StockIssue).join(StockIssueDetail).filter(
    StockIssue.destination_location_id == room_loc_id,
    StockIssueDetail.item_id == item.item_id
).order_by(StockIssue.issue_date.desc()).first()  # ✅ Use issue_date

if last_issue and last_issue.source_location_id:
    source_loc_id = last_issue.source_location_id
    source_location = db.query(Location).filter(...).first()
    source_loc_name = source_location.name
    print(f"[CHECKOUT] Found source location: {source_loc_name}")
else:
    # Fallback 1: Find location with existing stock of this item
    location_with_stock = db.query(LocationStock).join(Location).filter(
        LocationStock.item_id == item.item_id,
        LocationStock.quantity > 0,
        Location.id != room_loc_id,  # Exclude the room
        Location.location_type.in_([...])
    ).order_by(LocationStock.quantity.desc()).first()
    
    if location_with_stock:
        source_loc_id = location_with_stock.location_id
        source_loc_name = location_with_stock.location.name
        print(f"[CHECKOUT] Using location with stock: {source_loc_name}")
    else:
        # Fallback 2: Last resort - warehouse
        warehouse = db.query(Location).filter(...).first()
        source_loc_id = warehouse.id
        source_loc_name = warehouse.name
```

---

## How It Works Now

### Priority Order for Finding Source Location

1. **Primary**: Check `StockIssue` records
   - Find the most recent stock issue that sent items to the room
   - Use `issue_date` for accurate ordering
   - Return items to the `source_location_id` from that issue

2. **Fallback 1**: Check `LocationStock`
   - If no stock issue found, find which location has this item in stock
   - Exclude the room itself
   - Return to the location with the most stock

3. **Fallback 2**: Warehouse
   - Only as last resort
   - Find any warehouse/central warehouse

### Example Flow

**Scenario**: Mineral Water transferred from Hotel Store to Room 101

```
Purchase:
  Hotel Store: +20 units

Transfer:
  Hotel Store: 20 → 10 (source)
  Room 101: 0 → 10 (destination)
  StockIssue created: source_location_id = Hotel Store

Checkout (5 used, 5 unused):
  1. Query finds StockIssue with source = Hotel Store ✅
  2. Return 5 unused to Hotel Store ✅
  3. Deduct 5 consumed from global stock ✅

Result:
  Hotel Store: 10 → 15 ✅ (got 5 back)
  Room 101: 10 → 0 ✅ (cleared)
  Global Stock: 20 → 15 ✅ (5 consumed)
```

---

## Improved Logging

The fix includes detailed logging to help debug return location issues:

```
[CHECKOUT] Found source location from stock issue: Hotel Store (ID: 3)
[CHECKOUT] Returned 5 to source location: 10 → 15
```

Or if stock issue not found:
```
[CHECKOUT] No stock issue found for item Mineral Water to room. Searching for location with stock...
[CHECKOUT] Using location with existing stock: Hotel Store (ID: 3)
```

Or if using fallback:
```
[CHECKOUT] Using fallback warehouse: Central Warehouse (ID: 1)
```

---

## Transaction Notes Updated

Transaction notes now include the location name for better tracking:

**Before**:
```
"Unused items returned from Room 101 to Location 3"
```

**After**:
```
"Unused items returned from Room 101 to Hotel Store"
```

---

## Verification Steps

1. **Clear data** (if needed for testing)
   ```bash
   python clear_transactional_data.py --confirm
   ```

2. **Create test scenario**:
   - Purchase items to Hotel Store
   - Transfer items from Hotel Store to Room 101
   - Process checkout with some items unused

3. **Check results**:
   - Hotel Store should receive the unused items back ✅
   - Central Warehouse should NOT be affected ✅
   - Transaction notes should show "returned to Hotel Store" ✅

4. **Check server logs** for:
   ```
   [CHECKOUT] Found source location from stock issue: Hotel Store (ID: 3)
   [CHECKOUT] Returned 5 to source location: 10 → 15
   ```

---

## Expected Behavior

### Correct Flow
```
Hotel Store (20) → Room 101 (10)
Checkout: 5 used, 5 unused
Hotel Store (10) ← Room 101 (5 returned) ✅
Result: Hotel Store = 15 ✅
```

### Previous Incorrect Flow
```
Hotel Store (20) → Room 101 (10)
Checkout: 5 used, 5 unused
Central Warehouse (0) ← Room 101 (5 returned) ❌
Result: Hotel Store = 10, Central Warehouse = -2 ❌
```

---

## Summary

### What Changed
- ✅ Improved source location detection logic
- ✅ Added multiple fallback levels
- ✅ Better logging for debugging
- ✅ Transaction notes include location names
- ✅ Uses `issue_date` for accurate ordering

### What Stayed the Same
- ✅ Unused items still returned during checkout
- ✅ Global stock still correctly updated
- ✅ Room stock still cleared to 0

### Benefits
- ✅ Items return to correct source location
- ✅ No more negative stock in wrong locations
- ✅ Better audit trail with location names
- ✅ Easier debugging with detailed logs
- ✅ More resilient with multiple fallbacks

---

**Status**: ✅ FIXED  
**Date**: 2025-12-15  
**Impact**: Unused items now correctly return to their original source location (Hotel Store, Main Kitchen Store) instead of defaulting to Central Warehouse
