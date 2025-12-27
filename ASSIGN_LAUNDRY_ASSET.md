# How to Assign Laundry Assets to Rooms

There are two main ways to assign laundry assets (towels, linens, robes) to rooms, depending on your goal:

1.  **Daily Housekeeping & Guest Requests** (Recommended for Laundry):
    *   Use this for transient assignment (e.g., giving fresh towels to a guest).
    *   The system tracks these items through a "Clean -> Room -> Dirty -> Laundry" cycle.

2.  **Permanent Room Inventory**:
    *   Use this for items that permanently stay in the room (e.g., Curtains, Mattress Protectors).

---

## Method 1: Daily Service Assignment (Recommended for Laundry)

This method deducts items from your main inventory and assigns them to the room for the duration of the service/stay.

### Step 1: Configure the Service (One-time setup)
1.  Navigate to the **Services** page.
2.  Click **"Create Service"**.
3.  Name the service (e.g., "Daily Housekeeping" or "Extra Towel Request").
4.  In the **Inventory Items** section of the form:
    *   Click **"Add Item"**.
    *   Select your laundry asset (e.g., "Bath Towel").
    *   Set the **Standard Quantity** (e.g., 2).
5.  Save the Service.
    *   *Note: Ensure your Inventory Item has "Track Laundry Cycle" enabled in its settings for automatic return logic.*

### Step 2: Assign to Room
1.  Go to the **Services** page.
2.  Click **"Assign Service"**.
3.  Fill in the form:
    *   **Service**: Select the service you created (e.g., "Extra Towel Request").
    *   **Room**: Select the target room.
    *   **Employee**: Select the housekeeping staff responsible.
4.  **Add/Adjust Items**:
    *   The standard items will appear automatically.
    *   You can click **"Add Extra Inventory Item"** to add more specific items on the fly (e.g., 1 extra "Hand Towel").
5.  Click **"Assign"**.

**Result:** The items are deducted from the "Main Warehouse" stock and tracked as being in that Room. When the service is marked **Computed**, the system will automatically "collect" the dirty linens into the **Laundry** location (if "Track Laundry Cycle" is enabled on the item).

---

## Method 2: Permanent Asset Mapping

Use this if you want to record that "Room 101 *always* has 2 Pillows" as part of its fixed inventory.

1.  Navigate to the **Inventory** page.
2.  Go to the **Assets** or **Locations** tab.
3.  Select **"Assign Asset"** (or "Map Asset").
4.  Select:
    *   **Item**: The laundry asset (e.g., "Premium Pillow").
    *   **Location**: The specific Room (e.g., "Room 101").
    *   **Quantity**: The number of items permanently assigned.
5.  Save.
