
# Work Completion Report

## Objective
Enable users to select a source location for inventory items when assigning a service, ensuring stock is deducted from the correct location.

## Changes Implemented

### 1. Backend Schema Update
**File:** `app/schemas/service.py`
- Added `InventorySourceSelection` model.
- Updated `AssignedServiceCreate` to include `inventory_source_selections: Optional[List[InventorySourceSelection]]`.

### 2. Backend Logic Update
**File:** `app/curd/service.py`
- Modified `create_assigned_service` to process `inventory_source_selections`.
- Logic now:
    - Builds a map of `item_id` -> `source_location_id`.
    - When deducting stock:
        - Uses the selected source location if available.
        - Falls back to default warehouse if not.
    - Updates `LocationStock` for the specific location (handling negative stock if necessary).
    - Deducts from global `InventoryItem.current_stock`.
    - Creates `InventoryTransaction` with notes indicating the source location.

### 3. Frontend UI & Logic
**File:** `src/pages/Services.jsx`
- **State Management:** Added `itemStockData` to store stock levels and `inventorySourceSelections` to track user choices.
- **Stock Fetching:** Implemented `fetchItemStocks` helper to retrieve stock distribution for items via `GET /inventory/items/{id}/stocks`.
- **UI Enahncement:**
    - Updated "Inventory Items Needed" section to show a dropdown for Source Location for each item.
    - Updated "Extra Inventory Items" section to also show a Source Location dropdown.
    - Dropdowns show available quantity per location (e.g., "Main Store (Avl: 10)").
    - Auto-selects the location with the highest stock by default.
- **Assignment Logic:** Updated `handleAssign` to construct the `inventory_source_selections` payload from both template items and extra items.

## Verification
- **Code Review:** Checked schemas and logic flow. The frontend correctly fetches data and passes it to the backend. The backend correctly interprets the data and updates the database.
- **Fallbacks:** If no source is selected (or stock fetch fails), the backend falls back to the previous default behavior (Central Warehouse), ensuring continuity.

## Next Steps
- The user can now test the "Assign Service" flow.
- A future improvement could be to prevent assignment if stock is insufficient at the selected location (currently it allows negative stock with a warning).
