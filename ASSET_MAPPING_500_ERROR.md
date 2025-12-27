# Asset Mapping 500 Error - Troubleshooting Guide

## Error Summary
**Error**: POST http://localhost:8011/api/inventory/asset-mappings 500 (Internal Server Error)
**Location**: Inventory.jsx:2053
**When**: Creating a new asset mapping

## Request Details
The frontend sends:
```javascript
{
  item_id: parseInt(asset.item_id),
  location_id: parseInt(assetMappingForm.location_id),
  serial_number: asset.serial_number || null,
  quantity: parseFloat(asset.quantity) || 1,
  notes: asset.notes || null
}
```

## Backend Endpoint
**File**: `ResortApp/app/api/inventory.py`
**Line**: 1991-2019
**Function**: `create_asset_mapping`

## Possible Causes

### 1. Database Constraint Violation
- **Duplicate serial number**: If the serial number already exists
- **Unique constraint**: Check if there's a unique constraint on (item_id, location_id, serial_number)

### 2. Invalid Foreign Keys
- **item_id doesn't exist**: The inventory item ID is invalid
- **location_id doesn't exist**: The location ID is invalid

### 3. Missing User
- **assigned_by user not found**: Line 2002 tries to get the user who created the mapping
- If `current_user.id` is invalid, this could fail

### 4. Data Type Issues
- **quantity**: Should be a number
- **item_id/location_id**: Should be integers

## How to Debug

### Step 1: Check Backend Logs
Look at the terminal running `run_all.bat` for the full error traceback. The backend prints:
```python
traceback.print_exc()  # Line 2017
```

### Step 2: Check the Data Being Sent
Add a console.log before the API call:
```javascript
// In Inventory.jsx, line 2052
console.log("Creating asset mapping with data:", {
  item_id: parseInt(asset.item_id),
  location_id: parseInt(assetMappingForm.location_id),
  serial_number: asset.serial_number || null,
  quantity: parseFloat(asset.quantity) || 1,
  notes: asset.notes || null
});
```

### Step 3: Verify Database State
Check if:
- The item_id exists in `inventory_items` table
- The location_id exists in `locations` table
- The serial_number (if provided) doesn't already exist

### Step 4: Check CRUD Function
The endpoint calls:
```python
inventory_crud.create_asset_mapping(db, mapping_data, assigned_by=current_user.id)
```

Check `ResortApp/app/curd/inventory.py` for the `create_asset_mapping` function.

## Quick Fixes to Try

### Fix 1: Check if Item/Location Exists
Before creating, verify the IDs are valid:
```python
# In inventory.py, after line 1998
item = inventory_crud.get_item_by_id(db, mapping_data['item_id'])
if not item:
    raise HTTPException(status_code=404, detail=f"Item with ID {mapping_data['item_id']} not found")

location = inventory_crud.get_location_by_id(db, mapping_data['location_id'])
if not location:
    raise HTTPException(status_code=404, detail=f"Location with ID {mapping_data['location_id']} not found")
```

### Fix 2: Handle Duplicate Serial Numbers
```python
# Check for existing mapping with same serial number
if mapping_data.get('serial_number'):
    existing = db.query(AssetMapping).filter(
        AssetMapping.serial_number == mapping_data['serial_number'],
        AssetMapping.is_active == True
    ).first()
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Serial number {mapping_data['serial_number']} is already assigned"
        )
```

### Fix 3: Better Error Message
The current error message should show in the alert. Check what it says:
```
"Failed to save asset assignment: [error detail here]"
```

## Next Steps

1. **Check the backend terminal** for the full error traceback
2. **Look at the browser console** for the full error response
3. **Verify the data** you're trying to submit (item ID, location ID, serial number)
4. **Check the database** to ensure the item and location exist

## Common Solutions

### If "Item not found":
- Make sure you've created the inventory item first
- Check that the item_id is correct

### If "Location not found":
- Make sure you've created the location first
- Check that the location_id is correct

### If "Duplicate serial number":
- Use a different serial number
- Or remove the existing mapping first

### If "User not found":
- Make sure you're logged in
- Check that the authentication token is valid

## Related Files
- Frontend: `dasboard/src/pages/Inventory.jsx` (line 2053)
- Backend API: `ResortApp/app/api/inventory.py` (line 1991)
- Backend CRUD: `ResortApp/app/curd/inventory.py` (create_asset_mapping function)
- Model: `ResortApp/app/models/inventory.py` (AssetMapping model)
