# Quantity Validation Implementation Plan

## Overview
Apply unit-based quantity validation system-wide to ensure countable items (pcs, nos, units, etc.) only accept whole numbers.

## Utility Created
- **File**: `src/utils/quantityValidation.js`
- **Functions**:
  - `isCountableUnit(unit)` - Check if unit is countable
  - `getQuantityStep(unit)` - Get step value ("1" or "0.01")
  - `normalizeQuantity(value, unit)` - Validate and round if needed
  - `getMinQuantity(unit)` - Get minimum quantity
  - `formatQuantity(quantity, unit)` - Format for display
  - `getQuantityInputProps(unit, value, onChange)` - Get complete props object

## Files Updated

### ✅ Completed
1. **Bookings.jsx** (Line 1714-1730)
   - Room allocation quantity input
   - Status: DONE

### 🔄 To Update

2. **FoodOrders.jsx**
   - Food item quantity inputs
   - Extra inventory item quantity inputs
   - Ingredient quantity inputs
   - Lines to check: Search for quantity inputs

3. **Fooditem.jsx**
   - Ingredient quantity inputs in recipe creation
   - Lines to check: handleIngredientChange, ingredient forms

4. **Services.jsx**
   - Service inventory item quantity inputs
   - Line 2960+: handleAddInventoryItem

5. **Inventory.jsx** (if any quantity inputs exist)
   - Purchase quantity inputs
   - Stock adjustment inputs
   - Transfer quantity inputs

6. **Package.jsx**
   - Adult/children counts (already using parseInt, but should validate)
   - Max stay days

## Implementation Steps

For each file:
1. Import utility functions at top:
   ```javascript
   import { getQuantityStep, normalizeQuantity } from "../utils/quantityValidation";
   ```

2. Update quantity input fields:
   ```javascript
   <input
     type="number"
     step={getQuantityStep(item?.unit)}
     value={quantity}
     onChange={(e) => {
       const normalized = normalizeQuantity(e.target.value, item?.unit);
       setQuantity(normalized);
     }}
   />
   ```

3. For backend submissions, ensure values are already normalized

## Countable Units List
- pcs, nos, unit, units
- piece, pieces
- item, items
- box, boxes
- bottle, bottles
- can, cans
- packet, packets, pack, packs

## Testing Checklist
- [ ] Bookings - Room allocation
- [ ] Food Orders - Order items
- [ ] Food Items - Recipe ingredients
- [ ] Services - Inventory items
- [ ] Inventory - Purchases, transfers, adjustments
- [ ] Package - Guest counts

## Notes
- This ensures data integrity at the UI level
- Backend should also validate (add validation there if not present)
- Prevents issues like "92.5 TVs" or "2.02 bottles"
