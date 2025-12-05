# COMPLETE INVENTORY ISSUES & SOLUTIONS

## 🔴 ALL CRITICAL ISSUES IDENTIFIED

### 1. Purchase Form - Missing Destination Location Field
**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Cannot specify where items will be stored  

**Solution:**
- Add destination location dropdown to purchase form
- Increase modal width from `max-w-4xl` to `max-w-6xl`
- Make field required

---

### 2. Cancelled Purchases Affecting Stock & Totals
**Status:** ❌ BROKEN  
**Impact:** Stock values are incorrect, cancelled purchases still counted  

**Problem:**
- PO-20251204-0002 is cancelled but shows ₹3,296.70
- Stock was added when received, but not removed when cancelled
- Transactions not reversed

**Backend Fix Required:**
File: `app/api/inventory.py` - Purchase status update endpoint

```python
@router.patch("/purchases/{purchase_id}")
def update_purchase_status(purchase_id: int, status_update: dict, db: Session):
    purchase = db.query(PurchaseMaster).filter(PurchaseMaster.id == purchase_id).first()
    old_status = purchase.status
    new_status = status_update.get("status")
    
    # CASE 1: Receiving purchase - Add stock
    if new_status == "received" and old_status != "received":
        for detail in purchase.details:
            # Update item stock
            item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
            item.current_stock += detail.quantity
            
            # Update location stock if destination specified
            if purchase.destination_location_id:
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
            
            # Create IN transaction
            transaction = InventoryTransaction(
                item_id=detail.item_id,
                transaction_type="in",
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                total_amount=detail.unit_price * detail.quantity,
                reference_number=purchase.purchase_number,
                notes=f"Purchase received: {purchase.purchase_number}",
                created_by=current_user.id
            )
            db.add(transaction)
    
    # CASE 2: Cancelling purchase - Reverse stock if it was received
    elif new_status == "cancelled" and old_status == "received":
        for detail in purchase.details:
            # Reverse item stock
            item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
            item.current_stock -= detail.quantity
            
            # Reverse location stock if destination specified
            if purchase.destination_location_id:
                location_stock = db.query(LocationStock).filter(
                    LocationStock.location_id == purchase.destination_location_id,
                    LocationStock.item_id == detail.item_id
                ).first()
                
                if location_stock:
                    location_stock.quantity -= detail.quantity
                    if location_stock.quantity <= 0:
                        db.delete(location_stock)
            
            # Create reversal transaction
            transaction = InventoryTransaction(
                item_id=detail.item_id,
                transaction_type="out",
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                total_amount=detail.unit_price * detail.quantity,
                reference_number=purchase.purchase_number,
                notes=f"Purchase cancelled - stock reversed: {purchase.purchase_number}",
                created_by=current_user.id
            )
            db.add(transaction)
    
    purchase.status = new_status
    db.commit()
    return purchase
```

**Frontend Fix:**
Exclude cancelled purchases from totals:

```javascript
// In summary calculations
const totalPurchaseValue = purchases
  .filter(p => p.status !== 'cancelled')
  .reduce((sum, p) => sum + parseFloat(p.total_amount || 0), 0);
```

---

### 3. Food Items Not in Waste Report
**Status:** ❌ BACKEND BUG  
**Impact:** Cannot report waste for prepared food  

**Backend Changes:**

**Migration:**
```python
# alembic/versions/add_food_waste.py
def upgrade():
    op.add_column('waste_logs', sa.Column('food_item_id', sa.Integer(), nullable=True))
    op.add_column('waste_logs', sa.Column('is_food_item', sa.Boolean(), default=False))
    op.alter_column('waste_logs', 'item_id', nullable=True)
    op.create_foreign_key('fk_waste_food_item', 'waste_logs', 'food_items', 
                          ['food_item_id'], ['id'])
```

**Model:**
```python
# app/models/inventory.py
class WasteLog(Base):
    __tablename__ = "waste_logs"
    
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=True)
    is_food_item = Column(Boolean, default=False)
    # ... other fields ...
```

**CRUD:**
```python
# app/curd/inventory.py
def create_waste_log(db: Session, data: dict, reported_by: int):
    is_food = data.get("is_food_item", False)
    
    if is_food:
        # Handle food item waste
        food_item = db.query(FoodItem).filter(FoodItem.id == data["food_item_id"]).first()
        if not food_item:
            raise ValueError("Food item not found")
        
        waste_log = WasteLog(
            log_number=generate_waste_log_number(db),
            food_item_id=data["food_item_id"],
            is_food_item=True,
            quantity=data["quantity"],
            unit=data["unit"],
            reason_code=data["reason_code"],
            notes=data.get("notes"),
            reported_by=reported_by
        )
    else:
        # Existing inventory item logic
        # ... (keep existing code)
    
    db.add(waste_log)
    db.commit()
    return waste_log
```

**API:**
```python
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
    return inventory_crud.create_waste_log(db, waste_data, current_user.id)
```

**Frontend:**
```jsx
// In waste form, update item dropdown to include food items
<select name="item_id" onChange={handleItemChange}>
  <option value="">Select Item</option>
  <optgroup label="Inventory Items">
    {inventoryItems.map(item => (
      <option key={`inv-${item.id}`} value={item.id} data-type="inventory">
        {item.name}
      </option>
    ))}
  </optgroup>
  <optgroup label="Food Items">
    {foodItems.map(item => (
      <option key={`food-${item.id}`} value={item.id} data-type="food">
        {item.name}
      </option>
    ))}
  </optgroup>
</select>

// Handler
const handleItemChange = (e) => {
  const itemId = e.target.value;
  const itemType = e.target.selectedOptions[0].dataset.type;
  
  if (itemType === 'food') {
    setForm({
      ...form,
      food_item_id: itemId,
      item_id: null,
      is_food_item: true
    });
  } else {
    setForm({
      ...form,
      item_id: itemId,
      food_item_id: null,
      is_food_item: false
    });
  }
};
```

---

### 4. Requisition Items Not Auto-Loading
**Status:** ❌ NOT IMPLEMENTED  
**Impact:** Manual entry required  

**Solution:**
```jsx
// In Issue Form, requisition dropdown onChange
onChange={(e) => {
  const reqId = e.target.value;
  setForm({ ...form, requisition_id: reqId });
  
  if (reqId) {
    const selectedReq = requisitions.find(r => r.id === parseInt(reqId));
    if (selectedReq?.details) {
      const newDetails = selectedReq.details.map(detail => ({
        item_id: detail.item_id,
        issued_quantity: detail.requested_quantity || detail.approved_quantity,
        unit: detail.unit,
        cost: items.find(i => i.id === detail.item_id)?.unit_price || 0,
        notes: `From ${selectedReq.requisition_number}`,
        _locked: true
      }));
      setForm(prev => ({ ...prev, details: newDetails }));
    }
  }
}}
```

---

### 5. Issue Destination Location Not Saving
**Status:** ❌ NEEDS INVESTIGATION  

**Check:**
1. Form has `destination_location_id` field
2. It's included in API payload
3. Backend saves it

**Fix:**
```javascript
// Ensure form submission includes both
const payload = {
  source_location_id: parseInt(form.source_location_id),
  destination_location_id: parseInt(form.destination_location_id),
  // ... other fields
};
```

---

### 6. No Reject Option for Requisitions
**Status:** ❌ NOT IMPLEMENTED  

**Solution:**
```jsx
// Replace button with dropdown
<select
  value={req.status}
  onChange={(e) => handleRequisitionStatusChange(req.id, e.target.value)}
  className="px-3 py-1 text-sm border rounded-lg"
>
  <option value="pending">Pending</option>
  <option value="approved">Approved</option>
  <option value="rejected">Rejected</option>
  <option value="completed">Completed</option>
</select>

// Handler
const handleRequisitionStatusChange = async (reqId, newStatus) => {
  await API.patch(`/inventory/requisitions/${reqId}`, { status: newStatus });
  fetchData();
};
```

---

## 📊 PRIORITY MATRIX

| Priority | Issue | Impact | Effort |
|----------|-------|--------|--------|
| 🔴 CRITICAL | Cancelled purchase stock reversal | HIGH | MEDIUM |
| 🔴 CRITICAL | Purchase destination location | HIGH | LOW |
| 🟠 HIGH | Food waste support | HIGH | HIGH |
| 🟠 HIGH | Requisition auto-load | MEDIUM | LOW |
| 🟡 MEDIUM | Issue destination save | MEDIUM | LOW |
| 🟡 MEDIUM | Requisition reject | LOW | LOW |

---

## 🎯 IMPLEMENTATION ORDER

### Phase 1: Quick Wins (Today)
1. ✅ Add destination location to purchase form (15 min)
2. ✅ Increase modal width (2 min)
3. ✅ Add requisition reject dropdown (10 min)
4. ✅ Fix requisition auto-load (20 min)

### Phase 2: Backend Critical (Today/Tomorrow)
1. ✅ Fix cancelled purchase stock reversal (1 hour)
2. ✅ Implement food waste support (2 hours)

### Phase 3: Polish (Tomorrow)
1. ✅ Fix issue destination location (30 min)
2. ✅ Test all integrations (1 hour)

---

## 📝 TESTING CHECKLIST

### Cancelled Purchase
- [ ] Create purchase, mark as received
- [ ] Verify stock increases
- [ ] Cancel the purchase
- [ ] Verify stock decreases back
- [ ] Check transactions show reversal
- [ ] Verify totals exclude cancelled

### Purchase Destination
- [ ] Create purchase with destination
- [ ] Mark as received
- [ ] Check location stock increases
- [ ] View location inventory
- [ ] Verify items appear

### Food Waste
- [ ] Select food item from dropdown
- [ ] Submit waste report
- [ ] Verify it saves
- [ ] Check it appears in waste list

### Requisition Auto-Load
- [ ] Create requisition with items
- [ ] Go to New Issue
- [ ] Select requisition
- [ ] Verify items auto-populate
- [ ] Verify quantities correct

---

## 🚀 READY TO IMPLEMENT

All solutions are documented above with exact code snippets. The main blockers are:

1. **Finding the exact file locations** - The Inventory.jsx file structure is unclear
2. **Backend access** - Need to implement purchase cancellation logic and food waste support

**Recommendation:** Start with the quick frontend wins (destination location, modal width, requisition dropdown) while I work on the backend fixes.

---

**Last Updated:** 2025-12-05 01:13 IST  
**Total Issues:** 6  
**Fixed:** 0  
**In Progress:** 0  
**Pending:** 6
