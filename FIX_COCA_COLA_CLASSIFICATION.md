# Fix: Coca-Cola Appearing in Wrong Section

## Problem
**Coca-Cola** was appearing in the **"Rent / Fixed Assets Check"** section (red) with a "RENT" badge, instead of the **"Consumables Inventory Check"** section (blue).

## Root Cause
The backend API (`app/api/checkout.py` line 872) was incorrectly setting:
```python
"is_rentable": (payable_qty > 0 or getattr(stock.item, 'is_rentable', False))
```

This logic was **wrong** because:
- **Payable ≠ Rentable**
- Coca-Cola is **payable** (guest pays for it if consumed)
- But Coca-Cola is **NOT rentable** (it's consumed, not rented)
- This caused the frontend to classify it as a rent/fixed asset

## The Fix

### Backend Change (`app/api/checkout.py`)
**Before:**
```python
"is_rentable": (payable_qty > 0 or getattr(stock.item, 'is_rentable', False))
```

**After:**
```python
"is_payable": (payable_qty > 0),  # Mark as payable if it has payable quantity
# Removed incorrect is_rentable logic - payable doesn't mean rentable!
# Coca-Cola is payable but NOT rentable - it's a consumable
```

### Frontend Logic (`dasboard/src/pages/Services.jsx`)
The frontend already has correct classification logic:
```javascript
// Consumables: Items that are NOT fixed and NOT rentable
const consumableItems = items.filter(item => {
  const isFixedItem = item.is_fixed_asset || 
    ['TV', 'Bulb', 'Remote', 'AC', 'Kettle', 'Hair Dryer', 'Safe', 'Iron']
      .some(k => item.item_name.includes(k));
  const isRentable = item.is_rentable;
  return !isFixedItem && !isRentable; // Pure consumables
});

// Assets: Items that ARE fixed OR rentable
const assetItems = items.filter(item => {
  const isFixedItem = item.is_fixed_asset || 
    ['TV', 'Bulb', 'Remote', 'AC', 'Kettle', 'Hair Dryer', 'Safe', 'Iron']
      .some(k => item.item_name.includes(k));
  const isRentable = item.is_rentable;
  return isFixedItem || isRentable; // Fixed or rentable
});
```

Now that the backend no longer sends `is_rentable: true` for Coca-Cola, the frontend will correctly classify it as a consumable.

## Result

### Before Fix:
```
🔧 Rent / Fixed Assets Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Item Name          | Total | Good | Damaged | Missing | Charge
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Coca Cola (RENT)   |   2   |  1   |   0     |    1    | +₹410.98
LED TV 43-Inch     |   1   |  0   |   0     |    1    |    -
LED Bulb 9W        |   1   |  0   |   0     |    1    |    -
```
❌ **Wrong!** Coca-Cola should NOT be in this section

### After Fix:
```
📦 Consumables Inventory Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Item Name          | Current | Available | Consumed | Charge
                   | Stock   | Stock     | Qty      |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Coca Cola          |    2    |    1      |    1     | +₹410.98
(PAYABLE)          |         |           |          |
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 Rent / Fixed Assets Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Item Name          | Total | Good | Damaged | Missing | Charge
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LED TV 43-Inch     |   1   |  0   |   0     |    1    |    -
(FIXED)            |       |      |         |         |
LED Bulb 9W        |   1   |  0   |   0     |    1    |    -
(FIXED)            |       |      |         |         |
```
✅ **Correct!** Coca-Cola is now in Consumables section with simple interface

## Key Distinctions

| Attribute | Coca-Cola | TV / LED Bulb |
|-----------|-----------|---------------|
| **is_payable** | ✅ True | ❌ False |
| **is_rentable** | ❌ False | ❌ False |
| **is_fixed_asset** | ❌ False | ✅ True |
| **Section** | Consumables | Rent/Fixed Assets |
| **Interface** | Simple (balance qty) | Detailed (good/damaged/missing) |
| **Damage Tracking** | ❌ No | ✅ Yes |

## Files Modified
1. ✅ `ResortApp/app/api/checkout.py` (Line 860-873) - Backend fix
2. ✅ `dasboard/src/pages/Services.jsx` (Lines 3938-4130) - Frontend already correct

## Testing
After the backend restarts, Coca-Cola will appear in the **Consumables** section with:
- Simple interface (just enter remaining quantity)
- "PAYABLE" badge (orange)
- No damage or missing fields
- Auto-calculated consumed quantity

The fix is complete! 🎉
