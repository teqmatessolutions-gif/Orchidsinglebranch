# How to Create Inventory Audit Service Request

## Method 1: From Asset Audit Report (Current Implementation)

### Steps:
1. **Navigate to Reports**
   - Go to **Reports** > **Housekeeping & Facility** > **Asset Audit Report**

2. **View Assets**
   - The report shows all fixed assets with their mapped locations vs actual locations
   - Assets with "Mismatch" status indicate discrepancies

3. **Raise Service Request**
   - For each asset row, click the **"Raise Service"** button
   - This creates a service request with:
     - Type: `service`
     - Description: Includes asset name, code, and location
     - Room: Automatically finds a room associated with the asset's location

4. **Raise Maintenance Ticket**
   - Click the **"Maintenance"** button for maintenance-related issues
   - This creates a service request with:
     - Type: `maintenance`
     - Description: Includes asset details and status
     - Room: Automatically finds a room associated with the asset's location

## Method 2: Direct API Call

You can create an inventory audit service request directly via API:

### Endpoint:
```
POST /api/service-requests
```

### Request Body:
```json
{
  "room_id": 1,  // Required: Any room ID (used as placeholder)
  "request_type": "inventory_audit",  // or "service" or "maintenance"
  "description": "Inventory audit required for asset: TV (AST-TV-014) at location: Room 101. Status: Mismatch"
}
```

### Example using JavaScript:
```javascript
const serviceRequest = {
  room_id: 1,  // Get from /api/rooms endpoint
  request_type: "inventory_audit",
  description: "Inventory audit required for asset: TV (AST-TV-014) at location: Room 101"
};

await API.post('/service-requests', serviceRequest);
```

## Method 3: From Services Page

1. **Go to Services Page**
   - Navigate to **Services** in the sidebar

2. **Create Service Request**
   - Click "Create Service Request" or similar button
   - Fill in:
     - Room: Select any room (or use a default room)
     - Request Type: Select "inventory_audit" or "maintenance"
     - Description: Describe the inventory audit requirement

## Service Request Types

Available request types:
- `delivery` - Default for food/service delivery
- `service` - General service request
- `maintenance` - Maintenance/repair request
- `inventory_audit` - Inventory audit request (can be added)
- `cleaning` - Cleaning service request

## Current Implementation Details

### Asset Audit Report Buttons:
- **"Raise Service"** button:
  - Creates service request with type: `service`
  - Automatically finds room by matching `location_id` with `inventory_location_id`
  - Falls back to first available room if no match

- **"Maintenance"** button:
  - Creates service request with type: `maintenance`
  - Includes asset status in description
  - Same room matching logic

### Location Matching:
The system tries to:
1. Find a room with `inventory_location_id` matching the asset's `location_id`
2. If no match, uses the first available room
3. If no rooms exist, shows an error message

## Improving the Implementation

To add a specific "Inventory Audit" request type:

1. **Update Service Request Schema** (if needed):
   - The current schema supports any `request_type` string
   - You can use `"inventory_audit"` directly

2. **Add Inventory Audit Button** (Optional):
   - Add a third button "Audit" in the Asset Audit Report
   - Set `request_type: "inventory_audit"`

3. **Filter Service Requests**:
   - In the Services page, filter by `request_type: "inventory_audit"` to see all audit requests

## Best Practices

1. **Use Descriptive Descriptions**:
   - Include asset name, code, location, and issue
   - Example: "Inventory audit: TV (AST-TV-014) at Room 101 - Location mismatch detected"

2. **Assign to Correct Room**:
   - The system automatically matches rooms by location
   - Verify the room assignment is correct

3. **Track Status**:
   - Service requests start as "pending"
   - Update to "in_progress" when audit begins
   - Mark as "completed" when audit is done

4. **Link to Maintenance**:
   - If audit reveals issues, create a maintenance ticket
   - Reference the audit service request in the maintenance description

