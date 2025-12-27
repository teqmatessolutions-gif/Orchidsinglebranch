# FINAL SIMPLE SOLUTION - NO MANUAL SPLIT

## What You Want
- Add items with a quantity
- Mark ENTIRE quantity as either "Complimentary" OR "Payable" with a simple radio button
- See it correctly in "Current Room Items" display

## Implementation

### Step 1: Remove Manual Split UI
Remove the "Manual split" checkbox and the Complimentary Qty / Payable Qty input fields.

### Step 2: Add Simple Radio Button
After the "Total Quantity" field, add:

```javascript
<div className="mt-3">
  <label className="block text-xs font-medium text-gray-700 mb-2">
    Item Type
  </label>
  <div className="flex gap-4">
    <label className="flex items-center cursor-pointer">
      <input
        type="radio"
        name={`payable_${index}`}
        checked={!item.is_payable}
        onChange={() => updateAllocationItem(index, "is_payable", false)}
        className="w-4 h-4 text-green-600 mr-2"
      />
      <span className="text-sm font-medium text-green-700">
        ✓ Complimentary (Free)
      </span>
    </label>
    <label className="flex items-center cursor-pointer">
      <input
        type="radio"
        name={`payable_${index}`}
        checked={item.is_payable === true}
        onChange={() => updateAllocationItem(index, "is_payable", true)}
        className="w-4 h-4 text-orange-600 mr-2"
      />
      <span className="text-sm font-medium text-orange-700">
        💰 Payable (Charged)
      </span>
    </label>
  </div>
</div>
```

### Step 3: Update Submission Logic
The submission should create ONE detail record with the is_payable flag:

```javascript
issueDetails.push({
  item_id: itemId,
  issued_quantity: requestedQty,
  unit: selectedItem.unit || "pcs",
  batch_lot_number: null,
  cost: null,
  is_payable: item.is_payable || false,  // Use the radio button value
  notes: item.notes || "",
});
```

### Step 4: Backend (Already Works!)
The backend already reads `is_payable` correctly.

### Step 5: Display (Already Works!)
The API already calculates and returns complimentary_qty and payable_qty.

## Result
- User selects item
- Enters quantity (e.g., 5)
- Selects "Complimentary" or "Payable" radio button
- Submits
- Display shows: Complimentary: 5 pcs OR Payable: 5 pcs (depending on selection)
