# Asset Damage Reporting Feature

## Overview
This feature allows hotel staff to report damaged fixed assets (e.g., TV, furniture) during the room checkout inventory verification process. If an asset is marked as damaged, its replacement cost is automatically added to the guest's bill.

## Changes Implemented

### 1. Frontend: Billing Page (`Billing.jsx`)
- **Inventory Verification Modal:** Added a new modal that appears when clicking "Request Checkout" (or verifying inventory).
- **Fixed Assets Display:** The modal now lists all fixed assets assigned to the room (fetched from the backend).
- **Damage Reporting:** Staff can check a box to mark an asset as "Damaged" and provide notes (e.g., "Screen cracked").
- **Submission:** When confirmed, the list of damaged assets is sent to the backend.

### 2. Frontend: Services Page (`Services.jsx`)
- **Enhanced Verification:** Updated the existing "Verify Inventory" modal for Housekeeping tasks.
- **Fixed Assets Section:** Added a "Fixed Assets Check" section above the consumables list.
- **Data Integration:** Ensures that damages reported by housekeeping are also captured and sent to the billing system.

### 3. Backend: Checkout Logic (`app/api/checkout.py`)
- **Schema Update:** `InventoryCheckRequest` now accepts `asset_damages`.
- **Logic Update:** `check_inventory_for_checkout` processes the reported damages:
    - Adds `replacement_cost` to the total charges.
    - Flags the item as `is_fixed_asset`.
    - Stores the damage details in the checkout request's inventory data.
- **Bill Calculation:** The bill generation logic now includes `asset_damage_charges`.

## How to Test
1.  **Go to Billing:** Select a room with an active booking.
2.  **Request Checkout:** If not already requested, click "Request Checkout".
3.  **Verify Inventory:** Click "Verify Inventory" (or it usually prompts automatically/via button if pending).
4.  **Mark Damage:** In the modal, find a fixed asset (e.g., "Smart TV"), check "Is Damaged?", and add a note.
5.  **Confirm:** Submit the verification.
6.  **Get Bill:** Generate the bill for the room. You should see the asset's replacement cost listed under "Itemized Charges" or "Asset Damages".
