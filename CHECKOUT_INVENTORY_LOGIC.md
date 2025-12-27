# Checkout Inventory Logic - Complete Guide

## Overview
During checkout, the system handles three types of inventory items differently:

1. **Fixed Assets** (TV, LED Bulb) → Stay in room
2. **Consumables** (Coca-Cola, Snacks) → Return unused to warehouse
3. **Rentables** (if any) → Return to warehouse

## Item Classification

### 1. Fixed Assets
**Examples**: TV, LED Bulb, AC, Furniture, Kettle, Hair Dryer, Safe, Iron

**Characteristics**:
- `is_asset_fixed = True` OR
- Category classification = "Asset" OR "Fixed Asset" OR
- Item name contains keywords: TV, Bulb, Remote, AC, Kettle, Hair Dryer, Safe, Iron

**Checkout Behavior**:
- ✅ **STAY IN ROOM** - Do NOT clear room stock
- ✅ Track if damaged/missing for billing
- ✅ Charge guest for damage/missing
- ❌ Do NOT return to warehouse
- ❌ Do NOT deduct from global stock

**Example - Room 101**:
```
Before Checkout:
- LED TV 43-inch: 1 unit in room
- LED Bulb 9W: 1 unit in room

After Checkout:
- LED TV 43-inch: 1 unit STILL in room ✅
- LED Bulb 9W: 1 unit STILL in room ✅
```

### 2. Consumables
**Examples**: Coca-Cola, Snacks, Beverages, Toiletries

**Characteristics**:
- NOT fixed asset
- NOT rentable
- May be payable or complimentary

**Checkout Behavior**:
- ✅ Clear room stock to 0
- ✅ Return unused to warehouse
- ✅ Deduct consumed from global stock
- ✅ Charge for consumption beyond complimentary limit

**Example - Coca-Cola**:
```
Before Checkout:
- Room 102: 4 bottles (2 complimentary + 2 payable)

Staff Verification:
- Remaining: 3 bottles
- Consumed: 1 bottle

After Checkout:
- Room stock: 0 (cleared)
- Warehouse: +3 bottles (returned)
- Global stock: -1 bottle (consumed)
- Charge: ₹0 (within complimentary limit of 2)
```

### 3. Rentables
**Examples**: Extra pillows, blankets, portable heaters (if rented)

**Characteristics**:
- `is_rental = True` OR
- Category name contains "rental"

**Checkout Behavior**:
- ✅ Clear room stock to 0
- ✅ Return ALL to warehouse
- ✅ Charge rental fee if applicable

## Code Logic

### Backend (`app/api/checkout.py`)

```python
# Step 1: Classify item
is_fixed_asset = getattr(inv_item, 'is_asset_fixed', False)
is_rental = "rental" in inv_item.category.name.lower() if inv_item.category else False

# Step 2: Determine if should process return
should_process_return = True
if is_fixed_asset and not is_rental:
    should_process_return = False  # Fixed assets stay in room

# Step 3: Clear room stock (ONLY for consumables/rentables)
if room_stock_record and not is_fixed_asset:
    room_stock_record.quantity = 0  # Clear
    print(f"Cleared room stock for consumable/rentable")
elif room_stock_record and is_fixed_asset:
    # Keep stock as-is
    print(f"Keeping fixed asset in room: {inv_item.name}")

# Step 4: Return unused to warehouse (ONLY for consumables/rentables)
if unused_qty > 0 and source_loc_id and should_process_return:
    source_stock.quantity += unused_qty  # Return
    print(f"Returned {unused_qty} to warehouse")
```

### Frontend (`dasboard/src/pages/Services.jsx`)

Two separate sections in checkout modal:

**Consumables Section**:
```jsx
{consumableItems.length > 0 && (
  <div>
    <h3>Consumables Inventory Check</h3>
    {/* Simple interface: Enter remaining qty */}
  </div>
)}
```

**Rent/Fixed Assets Section**:
```jsx
{assetItems.length > 0 && (
  <div>
    <h3>Rent / Fixed Assets Check</h3>
    {/* Detailed interface: Track good/damaged/missing */}
  </div>
)}
```

## Checkout Flow Example

### Room 102 Checkout

**Initial Inventory**:
- LED TV 43-inch (Fixed): 1 unit
- LED Bulb 9W (Fixed): 1 unit  
- Coca-Cola (Consumable): 4 bottles (2 free + 2 paid)
- Mineral Water (Consumable): 2 bottles (complimentary)

**Staff Verification**:
1. **Fixed Assets**:
   - TV: Present ✅, Not damaged
   - LED Bulb: Present ✅, Not damaged
   
2. **Consumables**:
   - Coca-Cola: 3 bottles remaining → 1 consumed
   - Mineral Water: 1 bottle remaining → 1 consumed

**System Processing**:

```
Fixed Assets (TV, LED Bulb):
- Room stock: UNCHANGED (stays in room)
- Warehouse: NO RETURN
- Global stock: UNCHANGED
- Charge: ₹0 (no damage)

Consumables (Coca-Cola):
- Room stock: 4 → 0 (cleared)
- Warehouse: +3 bottles (returned)
- Global stock: -1 bottle (consumed)
- Charge: ₹0 (1 consumed < 2 complimentary limit)

Consumables (Mineral Water):
- Room stock: 2 → 0 (cleared)
- Warehouse: +1 bottle (returned)
- Global stock: -1 bottle (consumed)
- Charge: ₹0 (complimentary)
```

**Final State**:
```
Room 102 (After Checkout):
- LED TV 43-inch: 1 unit ✅ (STAYS)
- LED Bulb 9W: 1 unit ✅ (STAYS)
- Coca-Cola: 0 bottles (cleared)
- Mineral Water: 0 bottles (cleared)

Warehouse:
- Coca-Cola: +3 bottles (returned)
- Mineral Water: +1 bottle (returned)

Guest Bill:
- Room charges: ₹X
- Consumables: ₹0 (within limits)
- Asset damage: ₹0 (no damage)
- Total: ₹X
```

## Key Points

✅ **Fixed assets STAY in room** - TV, LED Bulb, etc. are permanent fixtures
✅ **Consumables cleared** - Room stock set to 0, unused returned to warehouse
✅ **Rentables returned** - All units returned to warehouse
✅ **Smart charging** - Only charge for consumption beyond limits or damage
✅ **Accurate tracking** - Global stock reflects actual consumption

## Files Modified
1. ✅ `ResortApp/app/api/checkout.py` (Lines 586-593) - Fixed asset logic
2. ✅ `dasboard/src/pages/Services.jsx` - Separate sections for different item types

The system now correctly handles all three types of inventory during checkout! 🎉
