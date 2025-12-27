# Billing & Checkout - Complete Guide

## Current Bill Structure

### What Should Appear in Bill

1. **Room Charges** - Base room rental
2. **Food Charges** - Food orders
3. **Service Charges** - Services (cleaning, laundry, etc.)
4. **Consumables Charges** - Payable consumables consumed beyond free limit
5. **Inventory Charges** - Rentable items + Payable consumables
6. **Asset Damage Charges** - Damaged/missing fixed assets

### What Should NOT Appear in Bill

- **Fixed Assets** (TV, LED Bulb) - Unless damaged or missing

## Item Types & Billing

### 1. Fixed Assets (TV, LED Bulb)
**Characteristics:**
- `is_asset_fixed = True` OR category is asset
- Permanent room fixtures
- `is_payable = False`
- `rental_price = None` or `0`

**Billing:**
- ❌ Do NOT show in bill normally
- ✅ ONLY show if damaged/missing
- Charge: Replacement cost (unit_price or selling_price)

**Example:**
```
Room has: 1 LED TV (₹10,000), 2 LED Bulbs (₹500 each)
Checkout: All present, no damage
Bill: (No mention of TV or bulbs)

If TV damaged:
Bill: Asset Damage - LED TV: ₹10,000
```

### 2. Consumables (Coca-Cola, Mineral Water)
**Characteristics:**
- NOT fixed asset
- `rental_price = None` or `0`
- May be `is_payable = True` (chargeable) or `False` (complimentary)
- Has `complimentary_limit`

**Billing:**
- ✅ Show if consumed beyond complimentary limit
- Charge: (consumed_qty - complimentary_limit) × unit_price

**Example:**
```
Room has: 5 Coca-Cola (2 complimentary @ ₹0, 3 payable @ ₹200 each)
Checkout: 3 consumed

Calculation:
- Consumed: 3
- Complimentary limit: 2
- Chargeable: max(0, 3 - 2) = 1
- Charge: 1 × ₹200 = ₹200

Bill: Consumables - Coca-Cola: 1 unit @ ₹200 = ₹200
```

### 3. Rentables (Kitchen Hand Towel, Extra Pillow)
**Characteristics:**
- NOT fixed asset
- `rental_price > 0` ✅ **This is the key!**
- `is_payable = True`
- Charged per unit or per day

**Billing:**
- ✅ ALWAYS show in bill
- Charge: rental_price × quantity

**Example:**
```
Room has: 1 Kitchen Hand Towel (rental_price = ₹120)
Checkout: Returned

Bill: Rentals - Kitchen Hand Towel: 1 unit @ ₹120 = ₹120
```

## Current Issue Analysis

### Room 101 Data:
```
1. LED TV 43-inch: is_payable=False, rental_price=None → Fixed Asset
2. LED Bulb 9W: is_payable=False, rental_price=None → Fixed Asset
3. Coca Cola 750ml: is_payable=True, rental_price=None → Consumable (Payable)
4. Mineral Water 1L: is_payable=False, rental_price=None → Consumable (Free)
5. Kitchen Hand Towel: is_payable=True, rental_price=₹120 → Rentable ✅
```

### Expected Bill:
```
Room Charges: ₹1,000.00

Inventory Charges: ₹120.00
  - Kitchen Hand Towel (Rental): 1 unit @ ₹120 = ₹120.00

Consumables Charges: ₹0.00 to ₹999.95 (depending on consumption)
  - Coca Cola: (if consumed beyond limit)

Grand Total: ₹1,120.00 + (consumables if any)
```

### Current Bill Shows:
```
Room Charges: ₹1,000.00
Consumables Charges: ₹0.00
Grand Total: ₹3,631.51 (incorrect!)
```

**Problem:** The ₹120 rental charge for Kitchen Hand Towel is not showing!

## Backend Logic (checkout.py lines 1936-1942)

```python
# Add rental charges for rentable assets
if rental_price and rental_price > 0:
    rental_charge = rental_price * detail.issued_quantity
    charges.inventory_charges = (charges.inventory_charges or 0) + rental_charge
    
    # Add to inventory usage with rental indicator
    charges.inventory_usage[-1]["rental_charge"] = rental_charge
    charges.inventory_usage[-1]["is_rental"] = True
```

**This logic is CORRECT!** It should add ₹120 to `charges.inventory_charges`.

## Possible Issues

### Issue 1: Frontend Not Displaying inventory_charges
The frontend might not be showing the `inventory_charges` field.

**Check:** `Billing.jsx` - Look for where charges are displayed

### Issue 2: Bill Calculation Not Running
The bill might be cached or not recalculating.

**Fix:** Clear checkout request and regenerate bill

### Issue 3: Data Not Saved
The `rental_price` might not be saved in the database.

**Verify:** Check if `rental_price=120` is actually in the StockIssueDetail record

## Debugging Steps

### Step 1: Verify Data
```sql
SELECT 
    sid.id,
    i.name,
    sid.issued_quantity,
    sid.is_payable,
    sid.rental_price,
    sid.unit_price
FROM stock_issue_details sid
JOIN inventory_items i ON sid.item_id = i.id
JOIN stock_issues si ON sid.issue_id = si.id
WHERE si.destination_location_id = 18  -- Room 101 location
```

### Step 2: Check Bill API Response
```bash
GET /api/bill/101
```

Look for:
```json
{
  "charges": {
    "inventory_charges": 120.0,  // Should be 120!
    "inventory_usage": [
      {
        "item_name": "Kitchen Hand Towel",
        "rental_price": 120.0,
        "rental_charge": 120.0,
        "is_rental": true
      }
    ]
  }
}
```

### Step 3: Check Frontend Display
In `Billing.jsx`, ensure it displays:
```jsx
{charges.inventory_charges > 0 && (
  <div>
    Inventory Charges: ₹{charges.inventory_charges}
  </div>
)}
```

## Solution Summary

**The backend logic is correct!** The issue is likely:

1. **Frontend not displaying `inventory_charges`** - Need to add display for this field
2. **Bill not including rental items in breakdown** - Need to show rentable items separately
3. **Fixed assets appearing in bill** - Need to filter them out from display

## Next Steps

1. ✅ Verify `rental_price=120` is in database
2. ✅ Check bill API response includes `inventory_charges: 120`
3. ✅ Update frontend to display inventory charges
4. ✅ Filter fixed assets from bill display
5. ✅ Show rentables and consumables separately

## Expected Final Bill

```
═══════════════════════════════════════════════════════════
                    DETAILED BILL
═══════════════════════════════════════════════════════════
Guest: GFSDGFG
Room: 101
Check-in: 17/16/2025
Check-out: 17/17/2025
Stay: 1 night

───────────────────────────────────────────────────────────
ROOM CHARGES
───────────────────────────────────────────────────────────
Room 101 (1 night)                              ₹1,000.00

───────────────────────────────────────────────────────────
RENTALS
───────────────────────────────────────────────────────────
Kitchen Hand Towel (1 unit @ ₹120)                ₹120.00

───────────────────────────────────────────────────────────
CONSUMABLES
───────────────────────────────────────────────────────────
Coca Cola 750ml (if consumed beyond limit)         ₹0.00

───────────────────────────────────────────────────────────
SUBTOTAL                                        ₹1,120.00
GST (12%)                                         ₹134.40
───────────────────────────────────────────────────────────
GRAND TOTAL                                     ₹1,254.40
═══════════════════════════════════════════════════════════

(Fixed assets like TV and LED Bulb do not appear)
```
