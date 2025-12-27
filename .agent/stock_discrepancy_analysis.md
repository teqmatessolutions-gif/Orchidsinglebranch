# Stock Discrepancy Analysis

## Problem Summary
There are discrepancies between stock used/unused quantities that don't reflect correctly across the system.

## Root Causes Identified

### 1. **Double Deduction Issue in Stock Transfers**
**Location**: `app/curd/inventory.py` - `create_stock_issue()` function (lines 610-737)

**Problem**:
- When stock is issued to a room (transfer), the system:
  - ✅ Deducts from source location stock (line 716)
  - ✅ Adds to destination location stock (line 694)
  - ❌ **ALSO deducts from global stock if no destination** (line 614)
  
**Impact**: Stock transfers between locations (warehouse → room) should NOT affect global stock, but the logic is inconsistent.

### 2. **Checkout Stock Return Logic Issues**
**Location**: `app/api/checkout.py` - `check_inventory_for_checkout()` function (lines 432-540)

**Problems**:
a) **Unused quantity calculation** (line 455):
   ```python
   unused_qty = max(0, allocated_stock - used_qty - missing_qty)
   ```
   - Uses `allocated_stock` from `LocationStock.quantity`
   - But this quantity may have already been modified by previous operations
   - No validation that allocated_stock matches what was originally issued

b) **Sequential stock modifications** (lines 474, 521, 526):
   ```python
   room_stock_record.quantity -= unused_qty  # Line 474
   # ... then later ...
   room_stock_record.quantity = 0  # Line 521
   # OR
   room_stock_record.quantity = max(0, remaining_stock - consumed_qty)  # Line 526
   ```
   - Multiple modifications to the same stock record
   - Logic branches can cause double-deductions

c) **Missing transaction validation**:
   - No check if stock has already been returned
   - No validation against original issue quantity

### 3. **LocationStock vs Global Stock Sync Issues**

**Problem**: The system maintains two parallel stock systems:
- `InventoryItem.current_stock` (global/total)
- `LocationStock.quantity` (per-location)

**Issues**:
- When purchases are received, both are updated (✅)
- When stock is issued/transferred:
  - Source location stock is deducted (✅)
  - Destination location stock is increased (✅)
  - Global stock is sometimes deducted (❌ - should only be for consumption, not transfers)
- When stock is returned at checkout:
  - Room stock is modified multiple times (❌)
  - Source stock is increased (✅)
  - Global stock is NOT updated (❌)

### 4. **No Audit Trail for Stock Movements**

**Problem**: While `InventoryTransaction` records exist, there's no:
- Linking between issue and return transactions
- Validation that returned quantity ≤ issued quantity
- Clear status tracking (issued → in-use → returned/consumed)

## Data Flow Issues

### Current Flow (BROKEN):
```
Purchase → Warehouse
  ├─ Global Stock +100 ✅
  └─ Location Stock (Warehouse) +100 ✅

Transfer to Room 101
  ├─ Global Stock -10 ❌ (should stay 100)
  ├─ Location Stock (Warehouse) -10 ✅
  └─ Location Stock (Room 101) +10 ✅

Checkout (Used: 3, Missing: 1, Unused: 6)
  ├─ Room Stock: 10 → 10-6 = 4 → 0 ❌ (multiple modifications)
  ├─ Warehouse Stock: 90 → 90+6 = 96 ✅
  └─ Global Stock: 90 (unchanged) ❌ (should be 96)
```

### Expected Flow (CORRECT):
```
Purchase → Warehouse
  ├─ Global Stock +100 ✅
  └─ Location Stock (Warehouse) +100 ✅

Transfer to Room 101
  ├─ Global Stock: 100 (unchanged) ✅
  ├─ Location Stock (Warehouse) -10 ✅
  └─ Location Stock (Room 101) +10 ✅

Checkout (Used: 3, Missing: 1, Unused: 6)
  ├─ Room Stock: 10 → 0 ✅ (clear room)
  ├─ Warehouse Stock: 90 → 96 ✅ (return unused)
  ├─ Global Stock: 100 → 96 ✅ (consumed 4 total)
  └─ Transactions:
      - Return: +6 to warehouse
      - Consumption: -4 from global (used + missing)
```

## Specific Issues Found

### Issue 1: Stock Issue Deducts Global Stock Incorrectly
**File**: `app/curd/inventory.py`, lines 610-615
```python
# CRITICAL FIX: Only deduct global stock if this is actual consumption (no destination)
# If there's a destination, it's a transfer - stock still exists, just moved locations
if not dest_location:
    # Actual consumption - deduct from global stock
    item.current_stock -= issued_qty
# else: Transfer between locations - global stock unchanged (just location stocks change)
```

**Problem**: The comment says it's correct, but `dest_location` is fetched from database and may be None even when `destination_location_id` exists. Need to check `data.get("destination_location_id")` instead.

### Issue 2: Checkout Logic Has Multiple Stock Modifications
**File**: `app/api/checkout.py`, lines 472-527

The logic has three different paths that modify `room_stock_record.quantity`:
1. Line 474: Deduct unused
2. Line 521: Set to 0 (if unused > 0)
3. Line 526: Deduct consumed (if unused == 0)

This creates confusion and potential for errors.

### Issue 3: No Validation of Stock Quantities
- No check that `used_qty + missing_qty + unused_qty == allocated_stock`
- No validation that stock hasn't already been processed
- No prevention of negative stock in critical paths

## Recommended Fixes

### Fix 1: Correct Global Stock Handling in Transfers
Ensure global stock is ONLY modified for:
- Purchases (increase)
- Consumption/waste (decrease)
- NOT for transfers between locations

### Fix 2: Simplify Checkout Stock Logic
Replace complex branching with single, clear logic:
```python
# 1. Calculate what should happen
allocated = room_stock_record.quantity
used = item.used_qty or 0
missing = item.missing_qty or 0
unused = max(0, allocated - used - missing)

# 2. Validate
if used + missing > allocated:
    # Log warning but allow (guest may have brought own items)
    pass

# 3. Execute stock movements atomically
# 3a. Clear room stock
room_stock_record.quantity = 0

# 3b. Return unused to source
if unused > 0:
    source_stock.quantity += unused

# 3c. Deduct consumed from global
consumed = used + missing
item.current_stock -= consumed

# 4. Record transactions
# - Return transaction for unused
# - Consumption transaction for used+missing
```

### Fix 3: Add Stock Movement Validation
- Create a `StockMovement` tracking table
- Link issues to returns
- Validate quantities at each step
- Prevent duplicate processing

### Fix 4: Add Stock Reconciliation Endpoint
Create an endpoint to:
- Recalculate global stock from location stocks
- Identify discrepancies
- Generate correction transactions
- Provide audit report

## Immediate Actions Needed

1. **Audit current stock data** - Check for discrepancies
2. **Fix stock issue logic** - Ensure transfers don't affect global stock
3. **Fix checkout logic** - Simplify and prevent double-deductions
4. **Add validation** - Prevent negative stock and invalid operations
5. **Create reconciliation tool** - Fix existing data issues
