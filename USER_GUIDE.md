# Resort Management Software - User Guide (End-to-End)

This guide provides a complete walkthrough of the **Resort Management System**, from initial setup to day-to-day operations and final reporting.

---

## 1. Initial Setup (One-Time Configuration)

Before guests arrive, set up your property details.

### 1.1 Configure Location & Rooms
**Go to:** `Room Management` (or `Create Rooms`)
1.  **Define Locations:** Go to *Inventory > Locations* first if you need specific buildings, but usually, you create rooms directly.
2.  **Add Rooms:**
    *   Click **"Add Room"**.
    *   Enter **Room Number** (e.g., 101, 205).
    *   Select **Type** (Single, Double, Suite) and **Price** (Per Night).
    *   Status starts as "Vacant".

### 1.2 Setup Inventory (Items & Stock)
**Go to:** `Inventory`
1.  **Create Categories:** (e.g., "Toiletries", "Linens", "Food Ingredients").
    *   *Tip:* Set "Track Laundry Cycle" for Linen categories.
2.  **Add Locations:**
    *   Create a **"Main Store"** (Type: Warehouse).
    *   Create a **"Laundry"** (Type: Laundry) - *Crucial for the Laundry Cycle*.
    *   Create **"Kitchen"** (Type: Department).
3.  **Add Items:**
    *   Click **"Add Item"**.
    *   Fill in Name, Category, Unit (pcs, kg).
    *   **Important Checkboxes:** 
        *   `Track Laundry Cycle?` for Towels/Sheets.
        *   `Is Perishable?` for Food.
    *   Set **Initial Stock** and **Unit Price**.

### 1.3 Configure Services
**Go to:** `Services`
1.  **Create Services:**
    *   Click **"Add New Service"**.
    *   Name: e.g., "Extra Bed", "Room Cleaning", "Laundry Service".
    *   Price: Enter the charge for the guest (or 0 if complimentary).
2.  **Link Inventory (Optional):**
    *   If a service uses items (e.g., "Towel Replacement"), link the "Bath Towel" item.
    *   This ensures stock is deducted when the service is performed.

---

## 2. The Guest Cycle (Day-to-Day Operations)

This is the core workflow for handling guests.

### 2.1 Check-In (Front Desk)
**Go to:** `Bookings`
1.  **New Booking:** Click **"Create Booking"**.
2.  **Guest Details:** Enter Name, Phone, ID Proof.
3.  **Selection:** Choose Check-in/Check-out dates and Select a **Room**.
4.  **Confirm:** Save the booking. The room status changes to **"Occupied"**.

### 2.2 During Stay (Services & Food)
Guests request services or order food.

**A. Assigning Services:**
**Go to:** `Services` or `Room Operations`
1.  Select the **Room**.
2.  Choose the **Service** (e.g., "Spa Treatment").
3.  Assign it.
4.  **Completion:** When done, mark status as **"Completed"**.
    *   *Automation:* If the service used Laundry items (marked in 1.2), the system automatically moves dirty linen to the "Laundry" location.

**B. Ordering Food (POS):**
**Go to:** `Restaurant / Food Orders`
1.  Select **Table** or **Room Service**.
2.  Add Items to the cart (e.g., "Burger", "Coffee").
3.  **Place Order:** This sends it to the Kitchen.
4.  **Billing:** Order cost is added to the Room Bill (if Room Service) or settled immediately.

### 2.3 Check-Out & Billing
**Go to:** `Billing`
1.  Select the **Room Number**.
2.  **Review Bill:** The system auto-calculates:
    *   Room Charges (Days x Price).
    *   Service Charges.
    *   Restaurant/Food Charges.
    *   Taxes (GST).
3.  **Generate Invoice:** Click **"Checkout"**.
4.  **Payment:** Record payment (Cash/Card/UPI).
5.  **Finish:** Room status changes to **"Dirty"** (or Vacant, depending on settings).

---

## 3. Back Office & Maintenance

### 3.1 The Laundry Cycle (Housekeeping)
**Go to:** `Inventory`
1.  **Checking Dirty Stock:**
    *   Go to *Stock Status*. Filter by Location: **"Laundry"**.
    *   You will see all dirty towels/sheets collected from rooms.
2.  **Processing (Washing):**
    *   (Physically wash the items).
3.  **Returning to Stock:**
    *   Go to *Stock Issue*.
    *   **Source:** "Laundry".
    *   **Destination:** "Main Store" (or specific Floor Store).
    *   Select Items and Quantity to return as Clean.

### 3.2 Procurement (Purchasing)
**Go to:** `Inventory`
1.  **Low Stock?** Create a **Purchase Order (PO)** to a Vendor.
2.  **Receiving:** When goods arrive, create a **GRN (Good Received Note)**.
3.  **Stock Up:** This automatically increases the count in "Main Store".

### 3.3 Employee Management
**Go to:** `Employees`
*   Add Staff, assign Roles (Manager, Receptionist, Housekeeping).
*   Track Payroll and Attendance.

---

## 4. Reports & Accounting

**Go to:** `Accounts`
1.  **Daily Sales:** View total revenue from Rooms and Restaurant.
2.  **GST Reports:** Generate GSTR-1 / GSTR-3B data.
3.  **Profit & Loss:** View Expenses vs. Income.

---

### Summary of Key Features
*   **Integrated Inventory:** Usage in Rooms/Restaurant auto-deducts stock.
*   **Automated Laundry:** Tracking cycle from Room -> Laundry -> Store.
*   **Unified Billing:** One final bill includes Stay + Food + Services.
*   **Role-Based Access:** Front desk sees Bookings; Kitchen sees Food Orders.
