# URGENT FIXES NEEDED - Inventory System

## 🔴 CRITICAL ISSUES TO FIX NOW

### Issue 1: Purchase Form Missing Destination Location Field
**Problem:** Backend has `destination_location_id` but frontend form doesn't show it  
**Impact:** Cannot specify where purchased items should be stored  

**What's Needed:**
1. Add "Destination Location" dropdown to purchase form
2. Make it a required field
3. Increase modal width from `max-w-4xl` to `max-w-6xl` for better readability

**Expected Location in Form:**
After "Payment Status" field, before "Purchase Items" section

**Code to Add:**
```jsx
<div>
  <label className="block text-sm font-bold text-gray-700 mb-1">
    Destination Location *
  </label>
  <select
    value={form.destination_location_id || ""}
    onChange={(e) => setForm({ ...form, destination_location_id: e.target.value })}
    className="w-full px-3 py-2 border-2 border-indigo-300 rounded-lg focus:ring-2 focus:ring-indigo-500 bg-indigo-50"
    required
  >
    <option value="">Select Destination Location</option>
    {locations
      .filter((loc) => loc.is_inventory_point)
      .map((loc) => (
        <option key={loc.id} value={loc.id}>
          {loc.name || `${loc.building} - ${loc.room_area}`}
        </option>
      ))}
  </select>
  <p className="text-xs text-gray-500 mt-1">
    Where items will be stored when received
  </p>
</div>
```

**Modal Width Change:**
```jsx
// Change from:
<div className="bg-white rounded-xl shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">

// To:
<div className="bg-white rounded-xl shadow-xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
```

---

### Issue 2: Items Not Reflecting in Location After Purchase
**Problem:** When purchase is received, items don't show up in the destination location  
**Impact:** Location stock tracking is broken  

**Root Cause:**
Backend needs to update `location_stocks` table when purchase status changes to "received"

**Backend Fix Needed:**
File: `app/api/inventory.py` or `app/curd/inventory.py`

When purchase status is updated to "received":
```python
# In purchase status update handler
if new_status == "received" and purchase.destination_location_id:
    # Update location stocks
    for detail in purchase.details:
        location_stock = db.query(LocationStock).filter(
            LocationStock.location_id == purchase.destination_location_id,
            LocationStock.item_id == detail.item_id
        ).first()
        
        if location_stock:
            location_stock.quantity += detail.quantity
        else:
            location_stock = LocationStock(
                location_id=purchase.destination_location_id,
                item_id=detail.item_id,
                quantity=detail.quantity
            )
            db.add(location_stock)
```

---

### Issue 3: Food Items Not Showing in Waste Report
**Problem:** Only inventory items appear, no prepared food items  
**Impact:** Cannot report waste for cooked dishes  

**Backend Changes Required:**

**1. Database Migration:**
```python
# alembic/versions/add_food_waste.py
def upgrade():
    op.add_column('waste_logs', sa.Column('food_item_id', sa.Integer(), nullable=True))
    op.add_column('waste_logs', sa.Column('is_food_item', sa.Boolean(), default=False))
    op.alter_column('waste_logs', 'item_id', nullable=True)
    op.create_foreign_key('fk_waste_food_item', 'waste_logs', 'food_items', 
                          ['food_item_id'], ['id'])
```

**2. Model Update:**
```python
# app/models/inventory.py - WasteLog class
class WasteLog(Base):
    # ... existing fields ...
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)  # Make nullable
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=True)  # Add this
    is_food_item = Column(Boolean, default=False)  # Add this
```

**3. API Endpoint Update:**
```python
# app/api/inventory.py
@router.post("/waste-logs")
def create_waste_log(
    item_id: Optional[int] = Form(None),
    food_item_id: Optional[int] = Form(None),
    is_food_item: bool = Form(False),
    # ... other fields ...
):
    waste_data = {
        "item_id": item_id,
        "food_item_id": food_item_id,
        "is_food_item": is_food_item,
        # ... other fields ...
    }
```

---

### Issue 4: Requisition Items Not Auto-Loading in Issue Form
**Problem:** When selecting a requisition, items don't populate automatically  
**Impact:** Manual entry required, time-consuming and error-prone  

**Frontend Fix Needed:**
In the Issue Form modal, update the requisition dropdown onChange:

```jsx
<select
  value={form.requisition_id}
  onChange={(e) => {
    const reqId = e.target.value;
    setForm({ ...form, requisition_id: reqId });
    
    // Auto-populate items from requisition
    if (reqId) {
      const selectedReq = requisitions.find(r => r.id === parseInt(reqId));
      if (selectedReq && selectedReq.details) {
        const newDetails = selectedReq.details.map(detail => ({
          item_id: detail.item_id.toString(),
          issued_quantity: detail.requested_quantity || detail.approved_quantity || 0,
          unit: detail.unit || 'pcs',
          batch_lot_number: '',
          cost: items.find(i => i.id === detail.item_id)?.unit_price || 0,
          notes: `From requisition ${selectedReq.requisition_number}`,
          _locked: true // Mark as locked
        }));
        setForm(prev => ({ ...prev, details: newDetails }));
      }
    }
  }}
>
```

---

### Issue 5: Issue Form - Destination Location Not Saving
**Problem:** Only source location saves, destination is lost  
**Impact:** Cannot track where items are going  

**Investigation Steps:**
1. Check if form has `destination_location_id` field
2. Verify it's included in API request payload
3. Check backend saves it correctly

**Likely Fix:**
Ensure form submission includes:
```javascript
const payload = {
  source_location_id: parseInt(form.source_location_id),
  destination_location_id: parseInt(form.destination_location_id), // Make sure this is included
  // ... other fields ...
};
```

---

### Issue 6: No Reject Option for Requisitions
**Problem:** Can only approve, cannot reject  
**Impact:** Invalid requisitions cannot be properly declined  

**Frontend Fix:**
Replace "Approve & Issue" button with status dropdown:

```jsx
<select
  value={req.status}
  onChange={(e) => handleRequisitionStatusChange(req.id, e.target.value)}
  className="px-3 py-1 text-sm border border-gray-300 rounded-lg"
>
  <option value="pending">Pending</option>
  <option value="approved">Approved</option>
  <option value="rejected">Rejected</option>
  <option value="completed">Completed</option>
</select>
```

Add handler:
```javascript
const handleRequisitionStatusChange = async (reqId, newStatus) => {
  try {
    await API.patch(`/inventory/requisitions/${reqId}`, { status: newStatus });
    addNotification({ 
      title: "Success", 
      message: `Requisition ${newStatus}`, 
      type: "success" 
    });
    fetchData();
  } catch (error) {
    addNotification({ 
      title: "Error", 
      message: "Failed to update status", 
      type: "error" 
    });
  }
};
```

---

## 📋 PRIORITY ORDER

1. **HIGHEST:** Add destination location to purchase form (user can't proceed without this)
2. **HIGH:** Fix items reflecting in location after purchase received
3. **HIGH:** Enable food waste reporting (backend changes)
4. **MEDIUM:** Auto-load requisition items in issue form
5. **MEDIUM:** Fix destination location in issues
6. **MEDIUM:** Add reject option for requisitions

---

## 🔍 WHERE TO FIND THE CODE

Since I cannot locate the exact code with searches, here's how to find it:

### Purchase Form:
1. Look for modal with title "New Purchase Order"
2. Search for: `PO Number`, `Vendor`, `Purchase Date`
3. Likely in a component that handles purchase creation
4. File might be: `Inventory.jsx` or a separate purchase modal component

### Issue Form:
1. Look for modal with title "New Stock Issue"
2. Search for: `Linked Requisition`, `Source Location`, `Destination Location`
3. Search for: `Issued Items` table

### Requisitions Table:
1. Look for table showing requisition list
2. Search for: `REQ-` (requisition numbers)
3. Search for: `ACTIONS` column header

---

## 🛠️ QUICK SEARCH COMMANDS

Try these searches in the codebase:

```bash
# Find purchase form
grep -r "PO Number" dasboard/src/pages/

# Find issue form  
grep -r "Issued Items" dasboard/src/pages/

# Find requisitions table
grep -r "REQ-" dasboard/src/pages/

# Find waste form
grep -r "Report Waste" dasboard/src/pages/
```

---

## ✅ WHAT'S ALREADY DONE

1. ✅ Purchase `destination_location_id` added to backend
2. ✅ Database migration executed
3. ✅ API returns `destination_location_name`
4. ✅ Asset price display fixed
5. ✅ Service soft delete implemented

---

**NEXT STEP:** Please share the file path or code section for the Purchase Form modal so I can add the destination location field and increase the width!
