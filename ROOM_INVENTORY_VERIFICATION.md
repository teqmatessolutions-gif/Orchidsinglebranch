# Room Inventory Verification Feature

## Overview
The **Room Inventory Verification** feature allows staff to verify the exact stock of all inventory items in a room during the checkout process. This includes tracking:
- **Fixed Assets:** Serialized items (e.g., TV, appliances) with their specific "Current Stock" (assigned) and "Available Stock" (actual).
- **Consumables:** Consumable items (e.g., amenities) with "Current Stock" and "Available Stock".

## Key Updates

### Backend (`app/api/checkout.py`)
- **Enhanced `get_pre_checkout_verification_data`**:
  - Now fetches room-specific `LocationStock` for consumables.
  - Now fetches `AssetRegistry` items for the room's location, including **Serial Numbers**.
  - Returns precise `current_stock` counts.

### Frontend (`Billing.jsx`)
- **Inventory Verification Modal**:
  - **Fixed Assets Table**:
    - Shows **Serial Number** for each asset.
    - Displays **Current Stock** (usually 1).
    - Allows inputting **Available Stock**.
    - If `Available < Current`, it highlights as missing/red.
    - Existing "Damaged" checkbox and Notes field remain.
  - **Consumables Table**:
    - Shows **Current Stock** (Assigned).
    - Allows inputting **Available Stock**.
    - Automatically calculates **Used/Missing** quantity based on the difference.
    - Displays **Potential Charge** based on usage beyond complimentary limits.

## User Flow
1. Select a Room/Booking in **Billing**.
2. Click **Request Checkout**.
3. In the **Verify Room Inventory** modal:
    - Review the list of Fixed Assets. Check Serial Numbers against physical items.
    - Enter `Available Stock` (1 if present, 0 if missing).
    - Review Consumables. Count physical stock and enter `Available Stock`.
    - The system calculates usage.
4. Add notes if needed and **Confirm Verification**.
5. Proceed to **Get Bill**. Any missing assets or chargeable consumables are added to the bill.
