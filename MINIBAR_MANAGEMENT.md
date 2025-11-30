# Minibar Management Guide

## Overview
Minibar items in rooms are managed through the Inventory Location system. Each room is linked to an inventory location, and items are issued to that location to stock the minibar.

## How to Add Minibar Items to Rooms

### Method 1: Through Room Booking (Allocation)
1. **Go to Bookings page**
2. **Select a booking** and open booking details
3. **Click "Add Allocation"** button
4. **Select items** from inventory (e.g., Water, Snacks, Beverages)
5. **Set quantities** for each item
6. **Choose if items are complimentary or payable**:
   - Items within the `complimentary_limit` are free
   - Items exceeding the limit are chargeable
7. **Submit** - Items will be issued to the room's inventory location

### Method 2: Direct Stock Issue to Room Location
1. **Go to Inventory page**
2. **Navigate to Stock Issues**
3. **Select the room's location** (each room has an inventory_location_id)
4. **Issue items** to that location
5. Items will appear in the room's inventory

## Setting Up Minibar Items

### 1. Create Inventory Items
- Go to **Inventory > Items**
- Create items like:
  - Water bottles
  - Soft drinks
  - Snacks
  - Alcohol (if applicable)

### 2. Configure Item Settings
- **`is_sellable_to_guest`**: Set to `true` for minibar items
- **`selling_price`**: Set the price guests will pay
- **`complimentary_limit`**: Set how many items are free (e.g., 2 water bottles)
- **`location`**: Can set default storage location

### 3. Link Rooms to Inventory Locations
- Each room should have an `inventory_location_id` that links to a Location
- Location type should be `GUEST_ROOM`
- Location name/room_area should match the room number

## Minibar Consumption Report

The **Minibar Consumption Report** shows:
- Items consumed from room minibars
- Which items exceeded the complimentary limit
- Chargeable amounts
- Room numbers and checkout dates

**Location**: Reports > Housekeeping & Facility > Minibar Consumption

## How It Works

1. **Stocking**: Items are issued to room locations via allocations or direct stock issues
2. **Consumption Tracking**: During checkout, staff verifies minibar items
3. **Billing**: Items consumed beyond the complimentary limit are charged to the guest
4. **Reporting**: The minibar consumption report shows all consumptions

## Best Practices

1. **Regular Stocking**: Stock minibars before guest check-in
2. **Check During Checkout**: Verify minibar items during checkout verification
3. **Set Complimentary Limits**: Configure reasonable free items (e.g., 2 water bottles)
4. **Price Items Appropriately**: Set selling prices that cover costs and provide margin
5. **Track Consumption**: Review minibar consumption reports regularly

## Adding Minibar Items to Other Locations

You can also add minibar items to:
- **Lobby areas**: Create a location with type `LOBBY` and issue items there
- **Restaurant**: Create a location with type `RESTAURANT` and issue items
- **Pool area**: Create a location with type `POOL` and issue items

The process is the same - create locations and issue inventory items to them.

