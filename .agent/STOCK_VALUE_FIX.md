# Stock Value vs Selling Price - Fix Documentation

## Issue
Stock value was being calculated using **selling price** instead of **cost price**, leading to inflated inventory valuations.

### Example of the Problem
- Item: Coca Cola 750ml
- Cost Price (Purchase): ₹20.00
- Selling Price: ₹199.99
- Quantity in Stock: 50

**Before Fix**:
- Stock Value = 50 × ₹199.99 = **₹9,999.50** ❌ (WRONG - using selling price)

**After Fix**:
- Stock Value = 50 × ₹20.00 = **₹1,000.00** ✅ (CORRECT - using cost price)

---

## What Was Fixed

### File: `app/api/inventory.py`
**Function**: `get_location_items()` (lines 1690-1720)

### Changes Made

#### Before (WRONG):
```python
# Used selling price for stock value calculation
final_unit_price = last_issue_price if last_issue_price > 0 else (
    item.selling_price if item.selling_price and item.selling_price > 0 
    else item.unit_price
)

items_dict[key] = {
    "unit_price": final_unit_price,
    "total_value": stock.quantity * (final_unit_price or 0),  # ❌ WRONG
    ...
}
```

#### After (CORRECT):
```python
# Separate selling price (for billing) from cost price (for stock value)
selling_unit_price = last_issue_price if last_issue_price > 0 else (
    item.selling_price if item.selling_price and item.selling_price > 0 
    else item.unit_price
)

# IMPORTANT: Stock value should ALWAYS use cost price
cost_price = item.unit_price or 0
stock_value = stock.quantity * cost_price

items_dict[key] = {
    "unit_price": selling_unit_price,      # For billing/display
    "cost_price": cost_price,              # Actual cost for valuation
    "selling_price": item.selling_price,   # Selling price if set
    "total_value": stock_value,            # ✅ CORRECT - uses cost
    ...
}
```

---

## Key Principles

### 1. Stock Value = Cost Price × Quantity
**Purpose**: Inventory valuation for accounting  
**Uses**: 
- Balance sheet reporting
- Inventory value tracking
- Cost of goods sold (COGS) calculations
- Stock reconciliation

**Formula**: `stock_value = quantity × unit_price (cost)`

### 2. Selling Price = Separate Field
**Purpose**: Revenue calculation and billing  
**Uses**:
- Guest billing
- Revenue projections
- Profit margin calculations
- Pricing display

**Formula**: `revenue = quantity × selling_price`

### 3. Profit = Selling Price - Cost Price
**Formula**: `profit = (selling_price - unit_price) × quantity`

---

## Impact

### Inventory Valuation
- **Before**: Inflated by selling price markup
- **After**: Accurate cost-based valuation

### Financial Reporting
- **Before**: Incorrect inventory asset value on balance sheet
- **After**: Correct inventory asset value

### Stock Reconciliation
- **Before**: Discrepancies due to mixed pricing
- **After**: Consistent cost-based tracking

---

## API Response Structure

### Endpoint: `GET /api/inventory/locations/{id}/items`

**Response for each item**:
```json
{
  "item_id": 19,
  "item_name": "Coca Cola 750ml",
  "current_stock": 50,
  "unit_price": 199.99,        // Selling/rental price (for billing)
  "cost_price": 20.00,         // Cost price (for stock valuation)
  "selling_price": 199.99,     // Selling price if set
  "total_value": 1000.00,      // Stock value (cost × quantity)
  ...
}
```

### Summary Fields:
```json
{
  "total_items": 50,
  "total_stock_value": 1000.00,  // Sum of all (cost_price × quantity)
  "items": [...]
}
```

---

## When to Use Each Price

### Use `cost_price` (unit_price) for:
- ✅ Stock value calculations
- ✅ Inventory valuation
- ✅ COGS calculations
- ✅ Purchase order tracking
- ✅ Stock reconciliation

### Use `selling_price` for:
- ✅ Guest billing
- ✅ Revenue calculations
- ✅ Pricing display to customers
- ✅ Profit margin analysis
- ✅ Sales reports

### Use `unit_price` field (in response) for:
- ✅ Display price (selling/rental)
- ✅ Billing calculations
- ✅ Guest-facing prices

---

## Verification

### Check Stock Value Calculation
1. Open Inventory Management
2. Click "View Items" for any location
3. Check "Stock Value" in modal header

**Expected**:
- Stock Value = Sum of (Cost Price × Quantity) for all items
- NOT based on selling price

### Example Verification
If you have:
- Item A: Cost ₹10, Selling ₹50, Qty 100
- Item B: Cost ₹20, Selling ₹80, Qty 50

**Stock Value should be**:
- (₹10 × 100) + (₹20 × 50) = ₹1,000 + ₹1,000 = **₹2,000**

**NOT**:
- (₹50 × 100) + (₹80 × 50) = ₹5,000 + ₹4,000 = ₹9,000 ❌

---

## Related Endpoints

All these endpoints correctly use cost price for stock value:

1. **`GET /api/inventory/locations/{id}/items`** ✅ FIXED
   - Stock value based on cost price
   - Selling price available separately

2. **`GET /api/inventory/stock-by-location`** ✅ Already Correct
   - Uses `item.unit_price` (cost) for valuation

3. **`GET /api/reports/inventory-valuation`** ✅ Already Correct
   - Uses `item.unit_price` (cost) for stock value

---

## Summary

### What Changed
- ✅ Stock value now uses **cost price** (unit_price)
- ✅ Selling price available as separate field
- ✅ Clear distinction between cost and selling price
- ✅ Accurate inventory valuation

### What Stayed the Same
- ✅ Billing still uses selling/rental price
- ✅ Guest-facing prices unchanged
- ✅ Revenue calculations unchanged

### Benefits
- ✅ Accurate inventory valuation
- ✅ Correct financial reporting
- ✅ Better cost tracking
- ✅ Proper profit margin calculations
- ✅ Compliance with accounting standards

---

**Status**: ✅ FIXED  
**Date**: 2025-12-15  
**Impact**: All inventory stock values now correctly reflect cost, not selling price
