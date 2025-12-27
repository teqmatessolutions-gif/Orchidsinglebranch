# Inventory Deduction Issue - Why Coca Cola Wasn't Deducted

## Problem

When a service was assigned to a room:
- ✅ **Mineral Water** was deducted from inventory
- ❌ **Coca Cola** was NOT deducted from inventory

Both items show "In Stock" but only water was consumed.

## Root Cause

### How Inventory Deduction Works

When you assign a service to a room (e.g., "Room Service", "Housekeeping"), the system:

1. **Checks which inventory items are linked to that service**
   - Looks in the `service_inventory_items` table
   - This table stores: `service_id`, `inventory_item_id`, `quantity`

2. **Deducts stock for linked items only**
   - For each item linked to the service:
     - Deducts `quantity` from `item.current_stock`
     - Creates an "out" transaction
     - Records the consumption

3. **Ignores items NOT linked to the service**
   - If an item is not in `service_inventory_items` for that service
   - No deduction happens

### Why Coca Cola Wasn't Deducted

**Scenario 1: Coca Cola is NOT linked to the service**
- The service you assigned (e.g., "Welcome Package") has Water in its inventory items
- But Coca Cola is NOT in the service's inventory items list
- Result: Water deducted ✅, Coca Cola ignored ❌

**Scenario 2: Different services were assigned**
- Service A (e.g., "Beverage Service") has Water → Water deducted
- Service B (e.g., "Snack Service") has Coca Cola → Coca Cola NOT assigned yet

## Solution

### Option 1: Add Coca Cola to the Service

If Coca Cola should be consumed when this service is assigned:

1. **Go to Services → Services tab**
2. **Find the service** that was assigned to the room
3. **Click Edit** on that service
4. **Add Coca Cola** to the inventory items list
5. **Set the quantity** (e.g., 1 bottle per service)
6. **Save the service**

Now when you assign this service to a room, both Water AND Coca Cola will be deducted.

### Option 2: Assign a Different Service

If Coca Cola should be consumed by a different service:

1. **Create or find a service** that includes Coca Cola
2. **Assign that service** to the room
3. Coca Cola will be deducted when that service is assigned

### Option 3: Manual Deduction

If you need to deduct Coca Cola manually:

1. **Go to Inventory → Transactions tab**
2. **Click "Add Transaction"**
3. **Select**:
   - Type: "Out" or "Consumption"
   - Item: Coca Cola 750ml
   - Quantity: (how many to deduct)
   - Reference: Room 102 (or whatever room)
   - Notes: "Manual consumption for Room 102"
4. **Save**

## How to Check Which Items Are Linked to a Service

### Method 1: Via UI
1. Go to **Services → Services tab**
2. Click **Edit** on the service
3. Scroll to **Inventory Items** section
4. You'll see which items are linked and their quantities

### Method 2: Via Database
```sql
-- Find which items are linked to a service
SELECT 
    s.name AS service_name,
    ii.name AS item_name,
    sii.quantity,
    ii.unit
FROM service_inventory_items sii
JOIN services s ON s.id = sii.service_id
JOIN inventory_items ii ON ii.id = sii.inventory_item_id
WHERE s.id = 1;  -- Replace with your service ID
```

### Method 3: Via Logs
When a service is assigned, the backend logs show:
```
[DEBUG] Found X inventory item associations for service Y
[DEBUG] Added inventory item: Water (ID: 23), Quantity: 1.0
[DEBUG] Deducted 1.0 pcs of Mineral Water 1L. New stock: 39.0
```

If Coca Cola doesn't appear in these logs, it's not linked to the service.

## Example Service Configuration

### Service: "Welcome Beverage Package"
**Inventory Items:**
- Mineral Water 1L → Quantity: 2
- Coca Cola 750ml → Quantity: 1
- Orange Juice 1L → Quantity: 1

**Result when assigned:**
- Water: 40 → 38 pcs (deducted 2)
- Coca Cola: 40 → 39 pcs (deducted 1)
- Orange Juice: 20 → 19 pcs (deducted 1)

## Verification Steps

1. **Check service configuration**:
   - Go to Services → Edit the service
   - Verify which items are in the inventory list

2. **Check backend logs**:
   - Look for `[DEBUG] Found X inventory item associations`
   - See which items were deducted

3. **Check transaction history**:
   - Go to Inventory → Transactions
   - Filter by item (Coca Cola)
   - See if there's an "out" transaction

## Summary

**Why Water was deducted:**
- Water is linked to the service in `service_inventory_items`
- When service was assigned → Water stock deducted ✅

**Why Coca Cola was NOT deducted:**
- Coca Cola is NOT linked to the service
- When service was assigned → Coca Cola ignored ❌

**Fix:**
- Add Coca Cola to the service's inventory items list
- OR assign a different service that includes Coca Cola
- OR manually create a consumption transaction

The system is working correctly - it only deducts items that are explicitly linked to the service being assigned.
