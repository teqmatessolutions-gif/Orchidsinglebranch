# Complimentary Items Charge Fix

## Issue
Complimentary items were showing **selling price** in the "POTENTIAL CHARGE" column during checkout verification, even though they should show ₹0.00 since they are complimentary.

### Example from Screenshot
- **Coca Cola 750ml**
  - Complimentary: 2 pcs
  - Payable: 0 pcs
  - **Potential Charge**: ₹199.99 ❌ (WRONG - should be ₹0.00)

---

## Root Cause

The checkout verification endpoint was not distinguishing between complimentary and payable items when calculating potential charges.

**Before Fix**:
- All items showed `charge_per_unit` × `current_stock`
- No distinction between complimentary vs payable
- Complimentary items incorrectly showed charges

---

## What Was Fixed

### File: `app/api/checkout.py`
**Function**: `get_pre_checkout_verification_data()` (lines 660-705)

### Changes Made

#### Before (WRONG):
```python
consumables.append({
    "item_name": stock.item.name,
    "current_stock": stock.quantity,
    "charge_per_unit": stock.item.selling_price or stock.item.unit_price,
    # ❌ No complimentary/payable breakdown
    # ❌ No potential_charge calculation
})
```

#### After (CORRECT):
```python
# Get stock issue details to determine complimentary vs payable
issue_details = db.query(StockIssueDetail).join(StockIssue).filter(
    StockIssueDetail.item_id == stock.item_id,
    StockIssue.destination_location_id == room.inventory_location_id
).all()

complimentary_qty = 0
payable_qty = 0

for detail in issue_details:
    if detail.is_payable:
        payable_qty += detail.issued_quantity
    else:
        complimentary_qty += detail.issued_quantity

# Calculate potential charge ONLY for payable items
selling_price = stock.item.selling_price or stock.item.unit_price or 0.0
potential_charge = payable_qty * selling_price  # ✅ Only payable items

consumables.append({
    "item_name": stock.item.name,
    "current_stock": stock.quantity,
    "complimentary_qty": complimentary_qty,  # ✅ NEW
    "payable_qty": payable_qty,              # ✅ NEW
    "charge_per_unit": selling_price,
    "cost_per_unit": stock.item.unit_price,  # ✅ NEW (for reference)
    "potential_charge": potential_charge,     # ✅ NEW (correct calculation)
})
```

---

## How It Works Now

### Complimentary Items
```json
{
  "item_name": "Coca Cola 750ml",
  "current_stock": 2,
  "complimentary_qty": 2,
  "payable_qty": 0,
  "charge_per_unit": 199.99,
  "potential_charge": 0.00  // ✅ 0 × ₹199.99 = ₹0.00
}
```

### Payable Items
```json
{
  "item_name": "Mineral Water 1L",
  "current_stock": 3,
  "complimentary_qty": 0,
  "payable_qty": 3,
  "charge_per_unit": 20.00,
  "potential_charge": 60.00  // ✅ 3 × ₹20.00 = ₹60.00
}
```

### Mixed Items (Some Complimentary, Some Payable)
```json
{
  "item_name": "Towel",
  "current_stock": 5,
  "complimentary_qty": 2,
  "payable_qty": 3,
  "charge_per_unit": 50.00,
  "potential_charge": 150.00  // ✅ 3 × ₹50.00 = ₹150.00
}
```

---

## Calculation Logic

### Potential Charge Formula
```
potential_charge = payable_qty × selling_price
```

**NOT**:
```
❌ potential_charge = current_stock × selling_price  (WRONG - includes complimentary)
❌ potential_charge = current_stock × cost_price     (WRONG - wrong price type)
```

### Key Points

1. **Complimentary Items** (`is_payable = false`)
   - No charge to guest
   - Included in package/complimentary allowance
   - `potential_charge = 0`

2. **Payable Items** (`is_payable = true`)
   - Guest will be charged
   - Beyond complimentary allowance
   - `potential_charge = payable_qty × selling_price`

3. **Selling Price vs Cost Price**
   - `charge_per_unit` = Selling price (what guest pays)
   - `cost_per_unit` = Cost price (what hotel paid)
   - Potential charge uses **selling price**

---

## API Response Structure

### Endpoint: `GET /api/bill/pre-checkout/{room_number}/verification-data`

**Response for each consumable**:
```json
{
  "item_id": 19,
  "item_name": "Coca Cola 750ml",
  "current_stock": 2,
  "complimentary_qty": 2,
  "payable_qty": 0,
  "complimentary_limit": 2,
  "charge_per_unit": 199.99,
  "cost_per_unit": 20.00,
  "potential_charge": 0.00,
  "unit": "pcs"
}
```

---

## Frontend Display

The frontend should now display:

| Item Name | Current Stock | Complimentary | Payable | Unit Price | Potential Charge |
|-----------|---------------|---------------|---------|------------|------------------|
| Coca Cola 750ml | 2 | 2 pcs | 0 pcs | ₹199.99 | **₹0.00** ✅ |
| Mineral Water 1L | 3 | 0 pcs | 3 pcs | ₹20.00 | **₹60.00** ✅ |
| Towel | 5 | 2 pcs | 3 pcs | ₹50.00 | **₹150.00** ✅ |

---

## Verification Steps

1. **Refresh your browser** (Ctrl+F5)
2. Go to **Services** or **Billing**
3. Click **"Verify Inventory"** for a room
4. Check the **"POTENTIAL CHARGE"** column

**Expected Results**:
- Complimentary items (0 payable): **₹0.00** ✅
- Payable items: **Correct charge** based on payable quantity ✅
- Mixed items: **Charge only for payable portion** ✅

---

## Related Fixes

This fix is part of a series of pricing fixes:

1. ✅ **Stock Value Fix** - Stock value uses cost price
2. ✅ **Unit Price Display Fix** - Unit price shows cost price by default
3. ✅ **Complimentary Charge Fix** - Complimentary items show ₹0 charge

---

## Summary

### What Changed
- ✅ Added `complimentary_qty` and `payable_qty` fields
- ✅ Added `potential_charge` field (calculated correctly)
- ✅ Added `cost_per_unit` for reference
- ✅ Potential charge now based on **payable quantity only**

### What Stayed the Same
- ✅ Selling price still used for billing
- ✅ Cost price available for reference
- ✅ Complimentary limits unchanged

### Benefits
- ✅ Accurate charge preview
- ✅ Clear distinction between complimentary and payable
- ✅ No confusion about what will be charged
- ✅ Proper guest billing

---

**Status**: ✅ FIXED  
**Date**: 2025-12-15  
**Impact**: Complimentary items now correctly show ₹0.00 potential charge, while payable items show accurate charges based on selling price
