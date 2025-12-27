# Stock Discrepancy Fixes - Implementation Guide

## Overview
This document describes the comprehensive fixes implemented to resolve stock discrepancies in the inventory system.

## Problems Fixed

### 1. ✅ Global Stock Deduction on Transfers (CRITICAL FIX)
**File**: `app/curd/inventory.py` - `create_stock_issue()` function

**Problem**: 
- When stock was transferred from warehouse to room, global stock was incorrectly deducted
- This caused global stock to not match the sum of location stocks
- Transfers should only move stock between locations, not reduce total inventory

**Solution**:
```python
# Now checks destination_location_id directly before deducting global stock
dest_location_id = data.get("destination_location_id")
if not dest_location_id:
    # Only deduct global stock for actual consumption (no destination)
    item.current_stock -= issued_qty
else:
    # Transfer - global stock unchanged
    print(f"[STOCK] Transfer: Moving {issued_qty} between locations (global stock unchanged)")
```

**Impact**: Global stock now correctly represents total inventory across all locations

---

### 2. ✅ Checkout Stock Logic Rewrite (CRITICAL FIX)
**File**: `app/api/checkout.py` - `check_inventory_for_checkout()` function

**Problem**:
- Multiple sequential modifications to room stock (lines 474, 521, 526)
- Complex branching logic caused double-deductions
- No validation of quantities
- Global stock not updated when items were consumed

**Solution**: Complete rewrite with atomic single-pass logic:

```python
# STEP 1: Validate quantities
allocated_stock = room_stock_record.quantity if room_stock_record else 0.0
used_qty = item.used_qty or 0.0
missing_qty = item.missing_qty or 0.0
unused_qty = max(0, allocated_stock - used_qty - missing_qty)
consumed_qty = used_qty + missing_qty

# Validation
if consumed_qty > allocated_stock:
    print(f"[WARNING] Consumed > Allocated - guest may have brought own items")
    unused_qty = 0

# STEP 2: Find source location for returns

# STEP 3: Execute stock movements atomically
# 3a. Clear room stock (ONE OPERATION)
room_stock_record.quantity = 0

# 3b. Return unused to source
if unused_qty > 0 and source_loc_id:
    source_stock.quantity += unused_qty
    # Record return transaction

# 3c. Deduct consumed from GLOBAL stock (CRITICAL)
if consumed_qty > 0:
    inv_item.current_stock -= consumed_qty
    # Record consumption transaction

# STEP 4: Calculate charges
```

**Impact**: 
- No more double-deductions
- Clear audit trail
- Global stock correctly updated
- Proper validation

---

### 3. ✅ Stock Reconciliation Tools (NEW FEATURE)
**File**: `app/api/stock_reconciliation.py` (NEW)

**Features**:

#### A. `/api/inventory/reconcile-stock` (POST)
Automatically fixes discrepancies between global and location stocks

**Usage**:
```bash
# Report only (don't fix)
POST /api/inventory/reconcile-stock?fix_discrepancies=false

# Fix discrepancies automatically
POST /api/inventory/reconcile-stock?fix_discrepancies=true
```

**Response**:
```json
{
  "timestamp": "2025-12-15T09:30:00",
  "total_items_checked": 150,
  "discrepancies_found": 12,
  "discrepancies_fixed": 12,
  "items_with_issues": [
    {
      "item_id": 45,
      "item_name": "Towel",
      "global_stock": 100,
      "total_location_stock": 95,
      "discrepancy": 5,
      "locations": [...],
      "action_taken": "Adjusted global stock from 100 to 95"
    }
  ],
  "summary": {
    "status": "Fixed",
    "message": "Fixed 12 discrepancies"
  }
}
```

#### B. `/api/inventory/stock-audit` (GET)
Detailed audit showing transaction history and stock calculations

**Usage**:
```bash
# Audit specific item
GET /api/inventory/stock-audit?item_id=45

# Audit all items (limited to 100)
GET /api/inventory/stock-audit
```

**Response**:
```json
{
  "audit_date": "2025-12-15T09:30:00",
  "items_audited": 1,
  "results": [
    {
      "item_id": 45,
      "item_name": "Towel",
      "global_stock": 95,
      "calculated_from_transactions": 95,
      "total_location_stock": 95,
      "discrepancies": {
        "global_vs_calculated": 0,
        "global_vs_locations": 0,
        "calculated_vs_locations": 0
      },
      "transaction_count": 25,
      "location_count": 8,
      "locations": [...],
      "recent_transactions": [...]
    }
  ]
}
```

#### C. `/api/inventory/validate-checkout-stock` (POST)
Pre-checkout validation to catch issues before processing

**Usage**:
```bash
POST /api/inventory/validate-checkout-stock?room_number=101
```

**Response**:
```json
{
  "room_number": "101",
  "location_id": 45,
  "total_items": 5,
  "status": "ok",
  "issues": [],
  "warnings": [],
  "stock_summary": [
    {
      "item_id": 12,
      "item_name": "Soap",
      "current_stock": 2,
      "total_issued": 3,
      "status": "ok"
    }
  ]
}
```

---

## How Stock Now Works (Correct Flow)

### Purchase Flow
```
1. Purchase received → Warehouse
   - Global Stock: +100 ✅
   - Location Stock (Warehouse): +100 ✅
   - Transaction: "in" type
```

### Transfer Flow (Warehouse → Room)
```
2. Stock Issue to Room 101
   - Global Stock: UNCHANGED (still 100) ✅
   - Location Stock (Warehouse): -10 ✅
   - Location Stock (Room 101): +10 ✅
   - Transactions:
     * "transfer_out" from warehouse
     * "transfer_in" to room
```

### Checkout Flow
```
3. Checkout (Used: 3, Missing: 1, Unused: 6)
   
   Step 1: Validate
   - Allocated: 10
   - Used: 3
   - Missing: 1
   - Unused: 6 (calculated)
   - Consumed: 4 (used + missing)
   
   Step 2: Clear room stock
   - Room Stock: 10 → 0 ✅
   
   Step 3: Return unused to warehouse
   - Warehouse Stock: 90 → 96 ✅
   - Transaction: "return" type (+6)
   
   Step 4: Deduct consumed from global
   - Global Stock: 100 → 96 ✅
   - Transaction: "out" type (-4)
   
   Final State:
   - Global: 96 (100 - 4 consumed)
   - Warehouse: 96 (90 + 6 returned)
   - Room 101: 0
   ✅ Global = Sum of Locations
```

---

## Validation & Safety Features

### 1. Quantity Validation
- Checks if consumed > allocated
- Warns but allows (guest may have brought own items)
- Prevents negative unused quantities

### 2. Transaction Logging
All stock movements now create proper transactions:
- **Purchases**: "in" type
- **Transfers Out**: "transfer_out" type
- **Transfers In**: "transfer_in" type
- **Returns**: "return" type
- **Consumption**: "out" type
- **Adjustments**: "adjustment" type (reconciliation)

### 3. Audit Trail
Every transaction includes:
- Item ID
- Quantity
- Unit price
- Reference number
- Detailed notes
- User who created it
- Timestamp

---

## Testing & Verification

### Step 1: Run Reconciliation (Report Only)
```bash
POST /api/inventory/reconcile-stock?fix_discrepancies=false
```
This will show you all current discrepancies without fixing them.

### Step 2: Review Discrepancies
Check the response to understand what's wrong:
- Items with negative stock
- Global stock not matching location totals
- Missing transactions

### Step 3: Fix Discrepancies
```bash
POST /api/inventory/reconcile-stock?fix_discrepancies=true
```
This will automatically correct all discrepancies.

### Step 4: Verify Specific Items
```bash
GET /api/inventory/stock-audit?item_id=<ITEM_ID>
```
Check transaction history and stock calculations for specific items.

### Step 5: Test Checkout Flow
1. Create a test booking
2. Issue stock to room
3. Validate before checkout:
   ```bash
   POST /api/inventory/validate-checkout-stock?room_number=<ROOM>
   ```
4. Process checkout with used/unused quantities
5. Verify:
   - Room stock cleared
   - Unused returned to warehouse
   - Global stock reduced by consumed amount
   - Transactions recorded correctly

---

## Monitoring & Maintenance

### Daily Checks
Run reconciliation report to catch issues early:
```bash
POST /api/inventory/reconcile-stock?fix_discrepancies=false
```

### Weekly Audits
Full stock audit of high-value items:
```bash
GET /api/inventory/stock-audit
```

### Before Month-End
Run full reconciliation with fixes:
```bash
POST /api/inventory/reconcile-stock?fix_discrepancies=true
```

---

## Debug Logging

All stock operations now include detailed logging:

```
[STOCK] Transfer: Moving 10 of Towel between locations (global stock unchanged)
[CHECKOUT] Room 101 Item Towel: Allocated=10, Used=3, Missing=1, Unused=6, Consumed=4
[CHECKOUT] Cleared room stock: 10 → 0
[CHECKOUT] Returned 6 to source location: 90 → 96
[CHECKOUT] Deducted 4 from global stock: 100 → 96
```

Check server logs for these messages to trace stock movements.

---

## Summary of Changes

| File | Changes | Impact |
|------|---------|--------|
| `app/curd/inventory.py` | Fixed global stock deduction on transfers | Global stock now accurate |
| `app/api/checkout.py` | Rewrote checkout stock logic | No more double-deductions |
| `app/api/stock_reconciliation.py` | NEW - Reconciliation tools | Can fix existing issues |
| `app/main.py` | Registered reconciliation router | Endpoints now available |

---

## Next Steps

1. **Run initial reconciliation** to fix existing data
2. **Test checkout flow** with new logic
3. **Monitor logs** for any issues
4. **Set up periodic reconciliation** (weekly/monthly)
5. **Train staff** on new validation endpoints

---

## Support

If you encounter any issues:
1. Check server logs for detailed error messages
2. Run stock audit on affected items
3. Use reconciliation tool to fix discrepancies
4. Review transaction history for the item

All stock movements are now fully traceable and reversible through the transaction log.
