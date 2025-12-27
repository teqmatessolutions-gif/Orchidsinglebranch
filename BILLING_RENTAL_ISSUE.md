# Billing & Checkout Rental Charges Issue

## Problem Statement
The billing system is showing inventory items (LED TV, LED Bulb, Mineral Water, Coca-Cola) with "Rent" labels, but **no rental charges are being calculated** in the bill.

## Current Behavior
**Bill shows:**
- Room Charges: ₹1,000.00
- Consumables Charges: ₹0.00
- Items listed with "Rent" label but no charges
- Grand Total: ₹3,631.51

**Expected:**
- Rentable items (if any) should have rental charges
- Consumables should have usage charges (if consumed beyond complimentary limit)
- Fixed assets should have damage charges (if damaged)

## Root Cause Analysis

### 1. Item Classification Confusion
The system is labeling ALL items as "Rent" in the UI, but this is incorrect:

**Correct Classification:**
- **LED TV 43-inch**: Fixed Asset (not rentable, not consumable)
- **LED Bulb 9W**: Fixed Asset (not rentable, not consumable)
- **Mineral Water**: Consumable (not rentable, may be payable)
- **Coca-Cola 750ml**: Consumable (not rentable, may be payable)

### 2. Rental vs Payable Confusion
There's confusion between:
- **Rentable items**: Items rented to guests (e.g., extra pillows, portable heaters)
- **Payable consumables**: Items consumed by guests and charged (e.g., minibar items)
- **Fixed assets**: Permanent room fixtures (TV, LED bulbs)

### 3. Missing Rental Price Configuration
For an item to generate rental charges, it needs:
1. `is_payable = True` in StockIssueDetail
2. `rental_price > 0` in StockIssueDetail
3. Proper quantity tracking

## How Billing Should Work

### For Fixed Assets (TV, LED Bulb)
- **No rental charges** - these are permanent fixtures
- **Only charge if damaged or missing**
- Example: TV damaged → Charge replacement cost

### For Consumables (Coca-Cola, Mineral Water)
- **No rental charges** - these are consumed, not rented
- **Charge for consumption beyond complimentary limit**
- Example: 4 Coca-Cola consumed, 2 free → Charge for 2

### For Rentable Items (if any)
- **Charge rental fee per day/hour**
- Example: Extra pillow rented for 2 days @ ₹50/day → Charge ₹100

## Current Data Structure

### StockIssueDetail Fields:
```python
- item_id: int
- issued_quantity: float
- is_payable: bool  # Is this item chargeable?
- is_paid: bool  # Has guest paid for it?
- rental_price: float  # Rental price per unit (if rentable)
- unit_price: float  # Cost price
```

### Billing Logic:
```python
# For rentable items:
if rental_price and rental_price > 0:
    rental_charge = rental_price * issued_quantity
    
# For payable consumables:
if is_payable and not is_paid:
    consumed_qty = calculate_consumed()
    chargeable_qty = max(0, consumed_qty - complimentary_limit)
    usage_charge = chargeable_qty * unit_price
```

## Solution

### Step 1: Fix Item Classification
Update the UI to show correct item types:
- Fixed Assets → Show as "FIXED" (not "Rent")
- Consumables → Show as "CONSUMABLE" (not "Rent")
- Rentables → Show as "RENT" (only if actually rentable)

### Step 2: Fix Charge Calculation
Ensure billing logic correctly:
1. **Fixed Assets**: Only charge if damaged/missing
2. **Consumables**: Charge for consumption beyond limits
3. **Rentables**: Charge rental fee if `rental_price > 0`

### Step 3: Update Stock Issue Logic
When issuing items to rooms:
- **Fixed Assets**: `is_payable = False`, `rental_price = 0`
- **Consumables (free)**: `is_payable = False`, `rental_price = 0`
- **Consumables (payable)**: `is_payable = True`, `rental_price = 0`, use `unit_price` for charges
- **Rentables**: `is_payable = True`, `rental_price = X`, charge per day/hour

## Example Scenarios

### Scenario 1: Room with Fixed Assets Only
**Items:**
- 1 LED TV (fixed asset)
- 2 LED Bulbs (fixed assets)

**Checkout:**
- TV: Present, not damaged → No charge
- Bulbs: 1 present, 1 damaged → Charge ₹500 (replacement cost)

**Bill:**
- Room: ₹1,000
- Asset Damage: ₹500
- **Total: ₹1,500**

### Scenario 2: Room with Consumables
**Items:**
- 4 Coca-Cola (2 complimentary, 2 payable @ ₹100 each)
- 2 Mineral Water (complimentary)

**Checkout:**
- Coca-Cola: 1 remaining → 3 consumed
- Mineral Water: 0 remaining → 2 consumed

**Bill:**
- Room: ₹1,000
- Consumables: ₹100 (3 consumed - 2 free = 1 chargeable @ ₹100)
- **Total: ₹1,100**

### Scenario 3: Room with Rentables
**Items:**
- 1 Extra Pillow (rentable @ ₹50/day for 2 days)
- 1 Portable Heater (rentable @ ₹200/day for 1 day)

**Checkout:**
- Both returned in good condition

**Bill:**
- Room: ₹1,000
- Rentals: ₹300 (₹50×2 + ₹200×1)
- **Total: ₹1,300**

## Files to Check/Fix

1. **`app/api/checkout.py`** - Billing calculation logic
2. **`dasboard/src/pages/Billing.jsx`** - Bill display UI
3. **`app/curd/inventory.py`** - Stock issue creation
4. **`dasboard/src/pages/Services.jsx`** - Checkout inventory modal

## Immediate Action Required

1. **Verify current data**: Check what `is_payable` and `rental_price` values are set for the items in Room 101
2. **Fix classification**: Update UI to show correct item types (not all as "Rent")
3. **Fix charges**: Ensure billing logic calculates charges correctly based on item type
4. **Test**: Create test scenarios for each item type and verify charges

## Testing Checklist

- [ ] Fixed asset with no damage → No charge
- [ ] Fixed asset damaged → Damage charge applied
- [ ] Consumable within free limit → No charge
- [ ] Consumable beyond free limit → Usage charge applied
- [ ] Rentable item → Rental charge applied
- [ ] Mixed items → All charges calculated correctly
