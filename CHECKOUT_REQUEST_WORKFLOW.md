# Checkout Request Workflow - API Guide

## Overview
This document explains how to update checkout request status and get inventory item details.

## API Endpoints

### 1. Get Inventory Item Details
**Endpoint:** `GET /bill/checkout-request/{request_id}/inventory-details`

**Description:** Retrieves all inventory items currently allocated to the room for the checkout request, including complimentary and payable quantities.

**Response:**
```json
{
  "room_number": "004",
  "guest_name": "John Doe",
  "location_name": "Room 004",
  "items": [
    {
      "id": 1,
      "name": "Water Bottle",
      "item_code": "WB001",
      "current_stock": 3,
      "complimentary_qty": 2,
      "payable_qty": 1,
      "stock_value": 20.00,
      "unit": "pcs",
      "unit_price": 20.00
    }
  ]
}
```

**Frontend Usage:**
```javascript
const handleViewCheckoutInventory = async (checkoutRequestId) => {
  try {
    const res = await api.get(`/bill/checkout-request/${checkoutRequestId}/inventory-details`);
    setCheckoutInventoryDetails(res.data);
    setCheckoutInventoryModal(checkoutRequestId);
  } catch (error) {
    console.error("Failed to fetch inventory details:", error);
    alert(`Failed to load inventory details: ${error.response?.data?.detail || error.message}`);
  }
};
```

### 2. Assign Employee to Checkout Request
**Endpoint:** `PUT /bill/checkout-request/{request_id}/assign?employee_id={employee_id}`

**Description:** Assigns an employee to a checkout request and updates status to "in_progress".

**Response:**
```json
{
  "message": "Employee assigned successfully",
  "request_id": 1,
  "employee_id": 5,
  "employee_name": "John Employee",
  "status": "in_progress"
}
```

**Frontend Usage:**
```javascript
const handleAssignEmployeeToRequest = async (requestId, employeeId) => {
  try {
    // Check if this is a checkout request (ID > 1000000)
    if (requestId > 1000000) {
      const checkoutRequestId = requestId - 1000000;
      await api.put(`/bill/checkout-request/${checkoutRequestId}/assign?employee_id=${employeeId}`);
    } else {
      await api.put(`/service-requests/${requestId}`, { employee_id: employeeId });
    }
    fetchServiceRequests();
  } catch (error) {
    console.error("Failed to assign employee:", error);
    alert(`Failed to assign employee: ${error.response?.data?.detail || error.message}`);
  }
};
```

### 3. Complete Checkout Request (Update Status)
**Endpoint:** `POST /bill/checkout-request/{request_id}/check-inventory`

**Description:** Marks inventory as checked and completes the checkout request. Updates status to "completed".

**Query Parameters:**
- `inventory_notes` (optional): Notes about the inventory verification

**Response:**
```json
{
  "message": "Inventory checked and checkout request completed successfully",
  "request_id": 1,
  "status": "completed",
  "inventory_checked": true
}
```

**Frontend Usage:**
```javascript
const handleCompleteCheckoutRequest = async (checkoutRequestId, notes) => {
  try {
    await api.post(`/bill/checkout-request/${checkoutRequestId}/check-inventory`, null, {
      params: { inventory_notes: notes || "" }
    });
    alert("Checkout request completed successfully!");
    setCheckoutInventoryModal(null);
    setCheckoutInventoryDetails(null);
    fetchServiceRequests();
  } catch (error) {
    console.error("Failed to complete checkout request:", error);
    alert(`Failed to complete checkout request: ${error.response?.data?.detail || error.message}`);
  }
};
```

## Status Flow

1. **pending** - Initial status when checkout request is created
2. **in_progress** - When employee is assigned
3. **inventory_checked** - When inventory is checked but not yet completed (optional intermediate state)
4. **completed** - When inventory verification is complete
5. **cancelled** - If request is cancelled

## Complete Workflow Example

```javascript
// Step 1: View inventory details
const viewInventory = async (checkoutRequestId) => {
  const res = await api.get(`/bill/checkout-request/${checkoutRequestId}/inventory-details`);
  console.log("Inventory items:", res.data.items);
  // Display items in modal with complimentary/payable breakdown
};

// Step 2: Assign employee (optional, can be done from service requests table)
const assignEmployee = async (checkoutRequestId, employeeId) => {
  await api.put(`/bill/checkout-request/${checkoutRequestId}/assign?employee_id=${employeeId}`);
  // Status changes to "in_progress"
};

// Step 3: Complete verification
const completeVerification = async (checkoutRequestId, notes) => {
  await api.post(`/bill/checkout-request/${checkoutRequestId}/check-inventory`, null, {
    params: { inventory_notes: notes || "" }
  });
  // Status changes to "completed"
  // Now bill can be generated in Billing page
};
```

## Backend Implementation Details

### Inventory Details Logic
The endpoint calculates:
- **Complimentary Quantity**: Items marked as non-payable in `StockIssueDetail.notes`
- **Payable Quantity**: Items marked as payable in `StockIssueDetail.notes`
- **Stock Value**: Sum of (payable_qty × unit_price) for each item

### Status Update Logic
When completing checkout request:
- Sets `inventory_checked = True`
- Sets `inventory_checked_by` to current user
- Sets `inventory_checked_at` to current timestamp
- Sets `status = "completed"`
- Sets `completed_at` to current timestamp
- Stores `inventory_notes` if provided

## Frontend Integration Points

1. **Services Page** (`dasboard/src/pages/Services.jsx`):
   - Service Requests table shows checkout requests with yellow background
   - "Verify Inventory" button calls `handleViewCheckoutInventory`
   - Modal displays inventory details and allows completion

2. **Billing Page** (`dasboard/src/pages/Billing.jsx`):
   - Checks if checkout request is "completed" before allowing bill generation
   - Shows checkout request status banner

## Notes

- Checkout requests appear in service requests with ID offset (+1000000)
- Checkout requests are identified by `is_checkout_request: true` flag
- Only completed checkout requests allow bill generation
- Inventory details show real-time allocation status from room location


