# Implementation Plan - Remaining Billing & Checkout Fixes

## ✅ COMPLETED

### Fix 1: Fixed Assets Stay in Room
**File:** `ResortApp/app/api/checkout.py` (Line 598)
**Status:** ✅ DONE - Backend restart required

**Change:**
```python
# Added check to prevent returning fixed assets
if unused_qty > 0 and source_loc_id and not is_fixed_asset:
```

**Result:**
- TV and LED Bulb now stay in room after checkout
- Only consumables/rentables returned to warehouse

---

## ⏳ TO IMPLEMENT

### Fix 2: Display Rental Charges in Bill

**Problem:** Kitchen Hand Towel rental charge (₹120) calculated but not displayed.

**Backend:** Already correct (lines 1936-1942 in checkout.py)
```python
if rental_price and rental_price > 0:
    rental_charge = rental_price * detail.issued_quantity
    charges.inventory_charges += rental_charge
```

**Frontend Fix Needed:** `dasboard/src/pages/Billing.jsx`

#### Step 1: Find where bill charges are displayed
Search for: `charges.room_charges` or `Itemized Charges`

#### Step 2: Add display for inventory_charges
```jsx
{/* After Room Charges */}
{charges.inventory_charges > 0 && (
  <div className="charge-line">
    <span>Inventory Charges (Rentals & Consumables):</span>
    <span>₹{charges.inventory_charges.toFixed(2)}</span>
  </div>
)}
```

#### Step 3: Show detailed breakdown
```jsx
{/* Detailed Inventory Items */}
{charges.inventory_usage && charges.inventory_usage.length > 0 && (
  <div className="inventory-details">
    <h4>Inventory Items / Consumables / Rentals:</h4>
    {charges.inventory_usage
      .filter(item => {
        // Filter out fixed assets unless damaged
        const isFixedAsset = item.category?.toLowerCase().includes('asset') ||
                            item.category?.toLowerCase().includes('electronic');
        const isRental = item.rental_price && item.rental_price > 0;
        const isDamaged = item.is_damaged;
        
        // Show if: (rentable) OR (consumable) OR (fixed asset AND damaged)
        return isRental || !isFixedAsset || isDamaged;
      })
      .map((item, idx) => (
        <div key={idx} className="inventory-item">
          <span>{item.item_name}</span>
          <span>
            {item.quantity} {item.unit}
            {item.rental_price > 0 && ` @ ₹${item.rental_price} = ₹${item.rental_charge}`}
            {item.is_damaged && ` (DAMAGED - ₹${item.damage_cost})`}
          </span>
        </div>
      ))}
  </div>
)}
```

---

### Fix 3: Damage Tracking Implementation

**Problem:** Damage status not saved when marking items as damaged during checkout.

#### Backend Implementation

**File:** `ResortApp/app/api/checkout.py`

**Find the endpoint that processes inventory verification** (search for `InventoryCheckRequest` or `check-inventory`)

**Add damage processing:**
```python
@router.post("/checkout-request/{checkout_request_id}/check-inventory")
def check_inventory_for_checkout(
    checkout_request_id: int,
    request: InventoryCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... existing code ...
    
    # Process each item
    for item_check in request.items:
        # Find the StockIssueDetail for this item
        stock_issue_detail = db.query(StockIssueDetail).filter(
            StockIssueDetail.item_id == item_check.item_id,
            # ... filter by room/checkout
        ).first()
        
        if stock_issue_detail:
            # Save damage information
            if item_check.damage_qty > 0:
                stock_issue_detail.is_damaged = True
                stock_issue_detail.damage_notes = f"Damaged: {item_check.damage_qty} units"
                
                # Calculate damage charge
                inv_item = db.query(InventoryItem).filter(
                    InventoryItem.id == item_check.item_id
                ).first()
                
                if inv_item:
                    damage_cost = item_check.damage_qty * (inv_item.unit_price or 0)
                    
                    # Add to asset_damages list in checkout request
                    # (You may need to create a separate table for this)
    
    # Process asset_damages from request
    for damage in request.asset_damages:
        # Save damage record
        # This could be in CheckoutRequest or a separate AssetDamage table
        pass
    
    db.commit()
```

#### Frontend Implementation

**File:** `dasboard/src/pages/Services.jsx` (Checkout Inventory Modal)

**Ensure damage tracking UI is working:**
```jsx
{/* In the Fixed Assets section */}
<input
  type="number"
  value={item.damage_qty || 0}
  onChange={(e) => handleUpdateInventoryVerification(
    index,
    'damage_qty',
    e.target.value
  )}
  className="damage-input"
/>
```

**When submitting:**
```jsx
const handleCompleteCheckoutRequest = async (checkoutRequestId, notes) => {
  const items = checkoutInventoryDetails.items.map(item => ({
    item_id: item.item_id || item.id,
    used_qty: Number(item.used_qty || 0),
    missing_qty: Number(item.missing_qty || 0),
    damage_qty: Number(item.damage_qty || 0),  // Include damage_qty
  }));

  const assetDamages = checkoutInventoryDetails.fixed_assets
    .filter(asset => asset.is_damaged || asset.damage_qty > 0)
    .map(asset => ({
      item_name: asset.item_name,
      replacement_cost: Number(asset.replacement_cost || asset.unit_price || 0),
      notes: asset.damage_notes || ""
    }));

  await api.post(`/bill/checkout-request/${checkoutRequestId}/check-inventory`, {
    inventory_notes: notes || "",
    items: items,
    asset_damages: assetDamages
  });
};
```

---

### Fix 4: Show Damaged Status in Location Stock

**File:** `dasboard/src/pages/Inventory.jsx` (Location Stock Modal)

**Update the Items & Stock table:**
```jsx
<td className="px-3 py-2">
  {item.is_damaged ? (
    <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
      Damaged
    </span>
  ) : item.location_stock <= 0 ? (
    <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
      Out of Stock
    </span>
  ) : item.is_low_stock ? (
    <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
      Low Stock
    </span>
  ) : (
    <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
      In Stock
    </span>
  )}
</td>
```

---

## Testing Checklist

### Test 1: Fixed Assets Stay in Room ✅
1. Create booking for Room 107
2. Issue TV and LED Bulbs to room
3. Checkout room
4. **Verify:** TV and LED Bulbs still in Room 107 inventory
5. **Verify:** Central Warehouse does NOT show them returned

### Test 2: Rental Charges Display
1. Create booking for Room 107
2. Issue Kitchen Hand Towel (rental_price=₹120)
3. Checkout room
4. **Verify:** Bill shows "Inventory Charges: ₹120"
5. **Verify:** Breakdown shows "Kitchen Hand Towel: 1 unit @ ₹120 = ₹120"

### Test 3: Damage Tracking
1. Create booking for Room 107
2. Issue LED Bulb to room
3. During checkout inventory verification:
   - Mark LED Bulb as damaged (damage_qty=1)
   - Add damage notes
4. Complete checkout
5. **Verify:** Bill shows "Asset Damage - LED Bulb: ₹100"
6. **Verify:** Location stock shows LED Bulb status as "Damaged"

### Test 4: Consumables Charges
1. Create booking for Room 107
2. Issue 5 Coca-Cola (2 complimentary, 3 payable @ ₹200)
3. During checkout: Enter 2 remaining (3 consumed)
4. Complete checkout
5. **Verify:** Bill shows "Consumables: Coca-Cola - 1 unit @ ₹200 = ₹200"

---

## Files to Modify

### Backend
1. ✅ `ResortApp/app/api/checkout.py` (Line 598) - DONE
2. ⏳ `ResortApp/app/api/checkout.py` - Add damage processing in inventory check endpoint
3. ⏳ `ResortApp/app/models/inventory.py` - Verify damage fields exist (already done)

### Frontend
1. ⏳ `dasboard/src/pages/Billing.jsx` - Display inventory charges and filter fixed assets
2. ⏳ `dasboard/src/pages/Services.jsx` - Ensure damage tracking UI works
3. ⏳ `dasboard/src/pages/Inventory.jsx` - Show damaged status

---

## Priority Order

1. **HIGH:** Restart backend to apply fixed asset fix ✅
2. **HIGH:** Update Billing.jsx to display rental charges
3. **MEDIUM:** Implement damage tracking backend
4. **MEDIUM:** Update damage tracking frontend
5. **LOW:** Polish UI and add better filtering

---

## Quick Win: Display Inventory Charges

**Fastest fix to show rental charges:**

In `Billing.jsx`, find where charges are displayed and add:

```jsx
{charges.inventory_charges && charges.inventory_charges > 0 && (
  <div style={{padding: '8px 0', borderBottom: '1px solid #eee'}}>
    <span>Inventory/Rental Charges:</span>
    <span style={{float: 'right', fontWeight: 'bold'}}>
      ₹{charges.inventory_charges.toFixed(2)}
    </span>
  </div>
)}
```

This will immediately show the ₹120 rental charge!

---

## Notes

- Backend calculation for rentals is CORRECT
- Main issue is frontend display
- Damage tracking needs both backend + frontend work
- Fixed asset filter is critical for clean bill display
