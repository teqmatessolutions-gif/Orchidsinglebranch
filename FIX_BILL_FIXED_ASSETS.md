# Fix: Remove Fixed Assets from Bill Display

## Problem
Fixed assets (LED TV, LED Bulb) are appearing in the bill with "Rent" labels, but they should **NOT appear in the bill at all** unless damaged or missing.

## Current Behavior
**Bill shows:**
```
Inventory Items / Consumables / Fixed Assets:
- LED TV 43-inch (1 unit - Rent: 101 [12/16/2025])
- LED Bulb 9W (1 unit - Rent: 101 [12/16/2025])
- Mineral Water (4 units - Rent: 101 [12/16/2025])
- Coca Cola 750ml (4 units - Rent: 101 [12/16/2025])
- Kitchen Hand Towel (1 unit - Rent: 101 [12/16/2025])
```

## Expected Behavior
**Bill should show:**
```
Consumables:
- Coca Cola 750ml: 5 units consumed, 2 chargeable @ ₹199.99 = ₹399.98

Rentables:
- Kitchen Hand Towel: 1 unit @ ₹120.00 = ₹120.00

(Fixed assets like TV and LED Bulb should NOT appear unless damaged)
```

## Solution

### Step 1: Filter Fixed Assets from Bill Display

The bill should only show:
1. **Consumables** - If consumed beyond complimentary limit
2. **Rentables** - If rental_price > 0
3. **Fixed Assets** - ONLY if damaged or missing (with damage charge)

### Step 2: Update Bill Schema

The `BillBreakdown` schema has:
- `inventory_usage: List[dict]` - Currently shows ALL items
- `consumables_items: List[dict]` - Should show only chargeable consumables
- `asset_damages: List[dict]` - Should show only damaged/missing assets

### Step 3: Backend Logic

When building the bill, filter items:

```python
# For inventory_usage list (or better, separate lists):
bill_items = []

for stock_issue_detail in room_stock_issues:
    item = stock_issue_detail.item
    
    # Check if item is fixed asset
    is_fixed = item.is_asset_fixed or (item.category and item.category.is_asset_fixed)
    
    # Only add to bill if:
    # 1. NOT a fixed asset, OR
    # 2. IS a fixed asset but damaged/missing
    
    if not is_fixed:
        # Consumable or rentable - add to bill
        if stock_issue_detail.rental_price and stock_issue_detail.rental_price > 0:
            # Rentable item
            bill_items.append({
                "item_name": item.name,
                "quantity": stock_issue_detail.issued_quantity,
                "type": "Rentable",
                "rental_price": stock_issue_detail.rental_price,
                "charge": stock_issue_detail.rental_price * stock_issue_detail.issued_quantity
            })
        elif stock_issue_detail.is_payable:
            # Payable consumable
            consumed = calculate_consumed_qty(...)
            chargeable = max(0, consumed - item.complimentary_limit)
            if chargeable > 0:
                bill_items.append({
                    "item_name": item.name,
                    "consumed": consumed,
                    "chargeable": chargeable,
                    "type": "Consumable",
                    "unit_price": stock_issue_detail.unit_price,
                    "charge": chargeable * stock_issue_detail.unit_price
                })
    else:
        # Fixed asset - only add if damaged/missing
        if is_damaged or is_missing:
            bill_items.append({
                "item_name": item.name,
                "type": "Asset Damage",
                "damage_cost": item.unit_price,  # Replacement cost
                "notes": damage_notes
            })
```

### Step 4: Frontend Display

Update `Billing.jsx` to show items in separate sections:

```jsx
{/* Consumables Section */}
{charges.consumables_items && charges.consumables_items.length > 0 && (
  <div>
    <h4>Consumables</h4>
    {charges.consumables_items.map(item => (
      <div key={item.item_id}>
        {item.item_name}: {item.chargeable} units @ ₹{item.unit_price} = ₹{item.charge}
      </div>
    ))}
  </div>
)}

{/* Rentables Section */}
{charges.rentable_items && charges.rentable_items.length > 0 && (
  <div>
    <h4>Rentals</h4>
    {charges.rentable_items.map(item => (
      <div key={item.item_id}>
        {item.item_name}: {item.quantity} units @ ₹{item.rental_price} = ₹{item.charge}
      </div>
    ))}
  </div>
)}

{/* Asset Damages Section */}
{charges.asset_damages && charges.asset_damages.length > 0 && (
  <div>
    <h4>Asset Damages</h4>
    {charges.asset_damages.map(item => (
      <div key={item.item_name}>
        {item.item_name}: Replacement cost = ₹{item.replacement_cost}
        {item.notes && <p>{item.notes}</p>}
      </div>
    ))}
  </div>
)}

{/* DO NOT show fixed assets unless damaged */}
```

## Implementation Steps

1. **Find where bill items are collected** - Search for where `inventory_usage` or similar lists are populated
2. **Add filtering logic** - Filter out fixed assets unless damaged
3. **Update schema** - Separate `rentable_items` from `consumables_items`
4. **Update frontend** - Display items in appropriate sections
5. **Test** - Verify fixed assets don't appear unless damaged

## Test Cases

### Test 1: Fixed Assets Only (No Damage)
**Setup:**
- Room has: 1 TV, 2 LED Bulbs (all fixed assets)
- Checkout: All present, no damage

**Expected Bill:**
- Room charges: ₹1,000
- No inventory items listed
- **Total: ₹1,000**

### Test 2: Fixed Asset Damaged
**Setup:**
- Room has: 1 TV, 2 LED Bulbs
- Checkout: TV damaged (₹10,000 replacement)

**Expected Bill:**
- Room charges: ₹1,000
- Asset Damage: TV - ₹10,000
- **Total: ₹11,000**

### Test 3: Consumables Only
**Setup:**
- Room has: 5 Coca-Cola (2 free, 3 payable @ ₹200 each)
- Checkout: 3 consumed

**Expected Bill:**
- Room charges: ₹1,000
- Consumables: Coca-Cola - 1 chargeable @ ₹200 = ₹200
- **Total: ₹1,200**

### Test 4: Rentables Only
**Setup:**
- Room has: 1 Extra Pillow (₹50/day for 2 days)
- Checkout: Returned

**Expected Bill:**
- Room charges: ₹1,000
- Rentals: Extra Pillow - ₹100
- **Total: ₹1,100**

### Test 5: Mixed Items
**Setup:**
- 1 TV (fixed, no damage)
- 5 Coca-Cola (3 consumed, 1 chargeable)
- 1 Towel (rentable @ ₹120)

**Expected Bill:**
- Room charges: ₹1,000
- Consumables: Coca-Cola - ₹200
- Rentals: Towel - ₹120
- **Total: ₹1,320**
- *(TV should NOT appear)*

## Files to Modify

1. **Backend**: `app/api/checkout.py` or wherever bill is generated
2. **Schema**: `app/schemas/checkout.py` - Add `rentable_items` field
3. **Frontend**: `dasboard/src/pages/Billing.jsx` - Update display logic

## Priority
**HIGH** - This is a critical billing issue that affects guest experience and revenue accuracy.
