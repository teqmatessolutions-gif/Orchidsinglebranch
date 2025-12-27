# Consumables vs Fixed Assets - Checkout Inventory Clarification

## Issue Summary
The user reported confusion about how consumable items like **Coca-Cola** are handled during checkout inventory verification. The system was showing "CONSUMED / DAMAGED" which implied that consumables need damage reporting, but they don't.

## Key Distinctions

### Consumables (e.g., Coca-Cola, Snacks, Beverages)
- **Type**: Payable items that guests consume
- **Tracking**: Only track **remaining/balance quantity** (staff enters this)
- **Auto-calculation**: System calculates consumed qty = Current Stock - Available Stock
- **No damage reporting needed** - items are consumed, not damaged
- **No missing tracking** - doesn't make sense for consumables
- **Billing**: Charged based on quantity consumed (may have complimentary limits)

### Fixed Assets (e.g., TV, LED Bulb, Furniture)
- **Type**: Returnable items assigned to rooms
- **Tracking**: Track **presence, damage status, and missing items**
- **Damage reporting required** - need to know if item is damaged
- **Billing**: Charged for damage/replacement cost if damaged or missing
- **Return**: Expected to be present and in good condition

## Changes Made

### File: `dasboard/src/pages/Services.jsx` (Lines 3938-4010)

**Before:**
- Confusing headers: "Good / Current", "Consumed / Damaged", "Missing"
- Complex conditional logic mixing assets and consumables
- Staff had to enter consumed quantity manually

**After:**
1. **Added informational banner**:
   ```
   📦 For Consumables: Enter the remaining quantity (balance) in the "Available Stock" field. 
   The system will auto-calculate how much was consumed. No damage reporting needed for consumables.
   ```

2. **Simplified table headers**:
   - Item Name
   - Current Stock (read-only)
   - **Available Stock** (staff enters remaining qty)
   - **Consumed Qty** (auto-calculated, read-only)
   - Potential Charge

3. **Removed confusing columns**:
   - ❌ "Good / Current" (confusing)
   - ❌ "Consumed / Damaged" (mixed concepts)
   - ❌ "Missing" (doesn't apply to consumables)

4. **Simplified logic**:
   - Staff only enters how many items are left (Available Stock)
   - System auto-calculates: Consumed = Current - Available
   - Shows "PAYABLE" badge for chargeable items

### File: `dasboard/src/pages/Billing.jsx` (Lines 1891-1962)

Similar changes applied to the Billing page checkout inventory modal.

## How It Works Now

### For Consumables (Coca-Cola example):

**Scenario**: Room has 2 Coca-Cola bottles

1. **Current Stock**: Shows `2` (allocated to room)
2. **Available Stock**: Staff counts and enters `1` (one bottle remaining)
3. **Consumed Qty**: System auto-calculates `1` (2 - 1 = 1 consumed)
4. **Potential Charge**: 
   - If complimentary limit = 2 → No charge (within free limit)
   - If complimentary limit = 0 → Charge for 1 bottle
5. **No damage or missing fields** - not applicable

### For Fixed Assets (TV example):

Handled in a separate "Fixed Assets Check" section with:
- Present checkbox
- Damaged checkbox  
- Damage notes field
- Replacement cost

## User Workflow

### Checking Out a Room:
1. **Request Checkout** → Creates checkout request
2. **Verify Inventory** → Opens modal with:
   - **Consumables Section**: Count remaining items, system calculates consumption
   - **Fixed Assets Section**: Check for presence and damage
3. **Submit Verification** → Completes checkout request
4. **Get Bill** → Final bill includes consumable charges + asset damage charges

## Technical Details

### Auto-Calculation Logic
```javascript
// When staff enters available stock
onChange={(e) => {
  const val = Math.min(totalQty, Math.max(0, parseInt(e.target.value) || 0));
  handleUpdateInventoryVerification(idx, 'available_stock', val);
  // Auto-calculate consumed qty
  handleUpdateInventoryVerification(idx, 'used_qty', totalQty - val);
}}
```

### Charge Calculation
```javascript
// For consumables: charge for consumed > complimentary limit
const freeLimit = item.complimentary_limit || 0;
const chargeable = Math.max(0, consumedQty - freeLimit);
const chargeAmount = chargeable * price;
```

## Summary
✅ **Simplified Interface**: Staff only enters remaining quantity
✅ **Auto-Calculation**: System calculates consumed quantity automatically  
✅ **No Damage Fields**: Removed for consumables (not applicable)
✅ **No Missing Fields**: Removed for consumables (not applicable)
✅ **Clear Guidance**: Informational banner explains the process
✅ **Accurate Billing**: Charges based on consumption exceeding complimentary limits

The system now provides a clean, simple interface for tracking consumable usage without confusing damage or missing fields.


### For Fixed Assets (TV, LED Bulb example):
1. **Current**: Shows expected quantity (usually 1)
2. **Available**: Staff enters if item is present (0 or 1)
3. **Damaged?**: Checkbox to mark if damaged
4. **Notes**: Required if damaged - describe the damage
5. **Cost**: Shows replacement cost if damaged

## User Workflow

### Checking Out a Room:
1. **Request Checkout** → Creates checkout request
2. **Verify Inventory** → Opens modal with two sections:
   - **Fixed Assets**: Check for damage (TV, furniture, etc.)
   - **Consumables**: Count usage (Coca-Cola, snacks, etc.)
3. **Submit Verification** → Completes checkout request
4. **Get Bill** → Final bill includes consumable charges + asset damage charges

## Technical Details

### Backend Logic (No changes needed)
- Consumables are identified by `is_payable=True` or `consumption_type='consumable'`
- Fixed assets are tracked in `AssetRegistry` and `AssetMapping` tables
- Checkout endpoint: `/bill/checkout-request/{id}/check-inventory`

### Frontend Display
- **Billing.jsx** (lines 1891-1962): Consumables table with usage tracking
- **Billing.jsx** (lines 1826-1889): Fixed assets table with damage tracking
- Clear visual separation with different background colors and headers

## Summary
✅ **Consumables** (Coca-Cola): Track **usage only**, no damage reporting
✅ **Fixed Assets** (TV, LED): Track **presence and damage**, with damage notes
✅ **Clear UI**: Separate sections with explanatory text
✅ **Accurate billing**: Consumable charges + asset damage charges

The system now clearly distinguishes between consumable items that are used/consumed and fixed assets that can be damaged.
