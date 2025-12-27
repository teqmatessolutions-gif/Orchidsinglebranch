# SIMPLE COMPLIMENTARY/PAYABLE SOLUTION

## User Requirement
- Simple checkbox/radio to mark item as "Complimentary" OR "Payable"
- Display correctly in "Current Room Items" tab

## Implementation Plan

### 1. Frontend UI (Bookings.jsx - Add Items section)
Add a simple radio button group after the quantity field:

```javascript
<div className="mt-2">
  <label className="block text-xs font-medium text-gray-700 mb-1">
    Item Type
  </label>
  <div className="flex gap-4">
    <label className="flex items-center">
      <input
        type="radio"
        name={`item_type_${index}`}
        checked={!item.is_payable}
        onChange={() => updateAllocationItem(index, "is_payable", false)}
        className="mr-2"
      />
      <span className="text-sm text-green-700">Complimentary (Free)</span>
    </label>
    <label className="flex items-center">
      <input
        type="radio"
        name={`item_type_${index}`}
        checked={item.is_payable}
        onChange={() => updateAllocationItem(index, "is_payable", true)}
        className="mr-2"
      />
      <span className="text-sm text-orange-700">Payable (Charged)</span>
    </label>
  </div>
</div>
```

### 2. Backend (Already Working!)
The backend in `app/curd/inventory.py` already reads `is_payable` from the request:
```python
is_payable = detail_data.get("is_payable", False)
```

### 3. API Response (Already Working!)
The API in `app/api/inventory.py` already calculates complimentary/payable:
```python
if detail.is_payable:
    payable_qty += detail.issued_quantity
else:
    complimentary_qty += detail.issued_quantity
```

### 4. Display (Already Working!)
The "Current Room Items" tab already shows COMPLIMENTARY and PAYABLE columns.

## What's Needed
Just add the radio button UI in the "Add Items" form. The rest is already implemented!

## Location to Edit
File: `c:\releasing\orchid\dasboard\src\pages\Bookings.jsx`
Search for: The quantity input field in the "Add Items" section
Add: The radio button group right after it
