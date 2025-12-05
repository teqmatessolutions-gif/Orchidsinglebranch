# Current Issues Summary - Inventory Management

## 🔴 Critical Issues (Require Immediate Attention)

### 1. Food Items Not Showing in Waste Report
**Status:** ❌ BACKEND BUG (Documented but not fixed)  
**Impact:** Cannot report waste for prepared food items  

**Root Cause:**
- `WasteLog` model only has `item_id` field (for inventory items)
- No `food_item_id` or `is_food_item` fields
- Frontend sends food item data but backend rejects it

**Solution Required:**
See detailed implementation in `BACKEND_FIXES_SUMMARY.md`

**Quick Fix Steps:**
1. Add columns to `waste_logs` table:
   - `food_item_id` (Integer, nullable, FK to food_items)
   - `is_food_item` (Boolean, default false)
2. Make `item_id` nullable
3. Update backend CRUD to handle both types
4. Update API endpoint to accept `food_item_id` and `is_food_item`

---

### 2. Requisition Items Not Auto-Loading in Issue Form
**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Manual data entry required, prone to errors  

**Expected Behavior:**
When user selects a linked requisition in "New Stock Issue" form:
1. Items should automatically populate in the "Issued Items" table
2. Quantities should pre-fill from requisition
3. Item selection should be locked (cannot change items)
4. Cost should auto-populate

**Current Behavior:**
- Requisition can be selected
- Items table remains empty
- User must manually add each item

**Solution Needed:**
Add `onChange` handler to requisition dropdown that:
```javascript
onChange={(e) => {
  const reqId = e.target.value;
  if (reqId) {
    const selectedReq = requisitions.find(r => r.id === parseInt(reqId));
    if (selectedReq && selectedReq.details) {
      const newDetails = selectedReq.details.map(detail => ({
        item_id: detail.item_id,
        issued_quantity: detail.requested_quantity || detail.approved_quantity,
        unit: detail.unit,
        cost: items.find(i => i.id === detail.item_id)?.unit_price || 0,
        notes: `From requisition ${selectedReq.requisition_number}`,
        _locked: true
      }));
      setIssueForm({ ...issueForm, details: newDetails });
    }
  }
}}
```

---

### 3. Destination Location Not Saving in Issues
**Status:** ❌ BACKEND OR FRONTEND BUG  
**Impact:** Cannot track where items are being sent  

**Observed:**
- User can select "Destination Location" in form
- Only "Source Location" appears to save
- Destination location not displayed in issue details

**Investigation Needed:**
1. Check if `destination_location_id` is being sent in API request
2. Verify backend saves both source and destination
3. Check if issue details modal displays destination

**Possible Causes:**
- Frontend not sending `destination_location_id` in form submission
- Backend not saving the field
- Backend model missing `destination_location_id` field

---

### 4. No Reject Option for Requisitions
**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Cannot reject invalid requisitions  

**Current State:**
- Requisitions table shows "Approve & Issue" button
- No way to reject a requisition
- No status dropdown

**Required:**
Replace "Approve & Issue" button with status dropdown:
```jsx
<select 
  value={req.status}
  onChange={(e) => handleRequisitionStatusChange(req.id, e.target.value)}
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
  await API.patch(`/inventory/requisitions/${reqId}`, { status: newStatus });
  fetchData();
};
```

---

## ✅ Fixed Issues (From Previous Session)

### 1. Purchase Destination Location
**Status:** ✅ FIXED  
- Backend: Added `destination_location_id` to purchases
- Migration executed successfully
- Location now saves and displays

### 2. Asset Price Display
**Status:** ✅ FIXED  
- Shows "-" when price is null/undefined
- No more $0.00 or NaN

### 3. Service Soft Delete
**Status:** ✅ FIXED  
- Services marked as inactive instead of deleted
- Data preserved

---

## 📋 Action Plan

### Immediate Priority (Today)

**1. Fix Food Waste (Backend)**
- [ ] Create migration for `food_item_id` and `is_food_item`
- [ ] Update `WasteLog` model
- [ ] Update CRUD function
- [ ] Update API endpoint
- [ ] Test with food items

**2. Fix Requisition Auto-Load (Frontend)**
- [ ] Find Issue Form modal code
- [ ] Add onChange handler to requisition dropdown
- [ ] Implement item auto-population
- [ ] Lock item selection when requisition is linked
- [ ] Test with existing requisition

**3. Fix Destination Location (Investigation + Fix)**
- [ ] Check API request payload
- [ ] Verify backend model has field
- [ ] Ensure frontend sends destination_location_id
- [ ] Test save and display

**4. Add Requisition Reject Option (Frontend)**
- [ ] Replace button with status dropdown
- [ ] Add status change handler
- [ ] Test status updates

---

## 🔍 Investigation Notes

### File Structure Issue
The `Inventory.jsx` file appears to be different from expected:
- File size: 8942 lines
- Cannot find requisition/issue code with standard searches
- May have been refactored or is a different version

**Next Steps:**
1. Search for the actual location of requisition/issue forms
2. May be in separate component files
3. Check git history for recent changes

---

## 📁 Files to Modify

### Backend (Food Waste)
1. `alembic/versions/add_food_waste_support.py` - New migration
2. `app/models/inventory.py` - Update WasteLog model
3. `app/curd/inventory.py` - Update create_waste_log function
4. `app/api/inventory.py` - Update waste endpoint
5. `app/schemas/inventory.py` - Update WasteLog schemas

### Frontend (Requisition & Issues)
1. Find the actual Issue Form component
2. Find the Requisitions table component
3. Update requisition dropdown handler
4. Add status dropdown to requisitions table
5. Fix destination location submission

---

## 🧪 Testing Checklist

### Food Waste
- [ ] Select food item from dropdown
- [ ] Fill in waste details
- [ ] Submit waste report
- [ ] Verify it saves correctly
- [ ] Check it appears in waste list

### Requisition Auto-Load
- [ ] Create a requisition with 2-3 items
- [ ] Go to New Stock Issue
- [ ] Select the requisition
- [ ] Verify items auto-populate
- [ ] Verify quantities are correct
- [ ] Verify items are locked

### Destination Location
- [ ] Create new issue
- [ ] Select source and destination
- [ ] Submit issue
- [ ] View issue details
- [ ] Verify both locations display

### Requisition Reject
- [ ] View requisitions list
- [ ] Change status to "Rejected"
- [ ] Verify status updates
- [ ] Check status persists after refresh

---

## 💡 Recommendations

1. **Urgent:** Fix food waste backend - this is blocking waste reporting for prepared items
2. **High Priority:** Implement requisition auto-load - saves time and reduces errors
3. **Medium Priority:** Add reject option - improves workflow
4. **Medium Priority:** Fix destination location - important for tracking

---

## 📞 Need Help With

1. **Locating Issue Form Code** - Cannot find it in Inventory.jsx with standard searches
2. **Verifying Current Code Structure** - File may have been refactored
3. **Testing Food Waste Fix** - Need to verify food items table exists and has correct structure

---

**Last Updated:** 2025-12-05 01:11 IST  
**Session:** Inventory Fixes - Day 2
