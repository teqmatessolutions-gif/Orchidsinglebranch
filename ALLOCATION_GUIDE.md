# ALLOCATION COMPLIMENTARY/PAYABLE FIX - COMPLETE GUIDE

## Current Status
✅ Backend logic is CORRECT - uses `is_payable` from request
✅ Frontend submission logic is CORRECT - creates separate records
✅ API response includes `complimentary_qty` and `payable_qty`
✅ UI has manual split fields

## Remaining Issue
The UI fields don't auto-initialize when "Manual Split" checkbox is checked.

## How to Use (Current Workaround)
1. Add item (e.g., Mineral Water, quantity 15)
2. Check "Manual Split" checkbox
3. **MANUALLY enter** 5 in "Complimentary Qty" field
4. **MANUALLY enter** 10 in "Payable Qty" field
5. Click "Add 1 Item(s)"

## What Happens
- Backend receives TWO detail records:
  * Record 1: qty=5, is_payable=False
  * Record 2: qty=10, is_payable=True
- Database stores correctly
- Display shows: Complimentary: 5 pcs, Payable: 10 pcs

## To Improve UX (Optional Enhancement)
Add these quick action buttons in Bookings.jsx around line 1458:

```javascript
<div className="flex gap-2 mt-2">
  <button
    type="button"
    onClick={() => {
      updateAllocationItem(index, "complimentary_qty", item.quantity || 0);
      updateAllocationItem(index, "payable_qty", 0);
    }}
    className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded"
  >
    All Complimentary
  </button>
  <button
    type="button"
    onClick={() => {
      updateAllocationItem(index, "complimentary_qty", 0);
      updateAllocationItem(index, "payable_qty", item.quantity || 0);
    }}
    className="px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded"
  >
    All Payable
  </button>
  <button
    type="button"
    onClick={() => {
      const half = Math.floor((item.quantity || 0) / 2);
      updateAllocationItem(index, "complimentary_qty", half);
      updateAllocationItem(index, "payable_qty", (item.quantity || 0) - half);
    }}
    className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded"
  >
    Split 50/50
  </button>
</div>
```

## Testing Checklist
- [ ] Purchase items to add stock
- [ ] Create booking and check-in
- [ ] Allocate with manual split (5 comp + 10 pay)
- [ ] Verify "Current Room Items" shows correct breakdown
- [ ] Complete checkout
- [ ] Verify charges calculated correctly (only payable items charged)
