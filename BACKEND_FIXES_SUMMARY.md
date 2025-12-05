# Complete Backend Investigation Results

## ✅ Issue 1: Purchase Location - FIXED

**Problem:** Purchase location not being saved or displayed  
**Root Cause:** Missing `destination_location_id` field in database and model  
**Status:** ✅ COMPLETELY FIXED

**Changes Made:**
1. Added database column via migration
2. Updated model with field and relationship
3. Updated schemas to include location fields
4. Modified API to populate `destination_location_name`

---

## ✅ Issue 2: Waste Not Reflected on Item Page - WORKING CORRECTLY

**Problem:** User reported waste not updating item quantities  
**Investigation Result:** **Waste IS working correctly!**

**Evidence:**
```python
# File: app/curd/inventory.py, lines 631-632
# Deduct stock
item.current_stock -= data["quantity"]
```

The waste log creation:
1. ✅ Checks stock availability (line 610)
2. ✅ Deducts from `item.current_stock` (line 632)
3. ✅ Creates transaction record (lines 635-645)
4. ✅ Commits to database (line 647)

**Possible User Confusion:**
- Waste updates `current_stock`, not `quantity_on_hand`
- User might be looking at wrong field
- Or frontend might not be refreshing after waste submission

**Recommendation:** Check if frontend is:
1. Refreshing item list after waste submission
2. Displaying `current_stock` field correctly

---

## ❌ Issue 3: Food Waste Not Working - CONFIRMED BUG

**Problem:** Food waste (prepared items) cannot be logged  
**Root Cause:** WasteLog model only supports inventory items, not food items

**Current Model:**
```python
class WasteLog(Base):
    __tablename__ = "waste_logs"
    
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    # ❌ No food_item_id field
    # ❌ No is_food_item flag
```

**Frontend Sends:**
```javascript
{
  item_id: foodItemId,  // This is a FOOD item ID, not inventory item ID
  is_food_item: true,   // Backend ignores this
  quantity: 5,
  unit: "portions"
}
```

**What Happens:**
1. Frontend sends food item ID as `item_id`
2. Backend tries to find it in `inventory_items` table
3. **Fails** because food items are in `food_items` table
4. Returns error: "Item not found"

### Solution Required

**Option A: Modify WasteLog Model (Recommended)**

```python
class WasteLog(Base):
    __tablename__ = "waste_logs"
    
    id = Column(Integer, primary_key=True)
    log_number = Column(String, unique=True)
    
    # Support both inventory and food items
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=True)
    is_food_item = Column(Boolean, default=False)
    
    location_id = Column(Integer, ForeignKey("locations.id"))
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    reason_code = Column(String, nullable=False)
    action_taken = Column(String)
    notes = Column(Text)
    reported_by = Column(Integer, ForeignKey("users.id"))
    waste_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship("InventoryItem", foreign_keys=[item_id])
    food_item = relationship("FoodItem", foreign_keys=[food_item_id])
    location = relationship("Location")
    reporter = relationship("User")
```

**Migration:**
```python
def upgrade():
    op.add_column('waste_logs', sa.Column('food_item_id', sa.Integer(), nullable=True))
    op.add_column('waste_logs', sa.Column('is_food_item', sa.Boolean(), default=False))
    op.alter_column('waste_logs', 'item_id', nullable=True)  # Make nullable
    op.create_foreign_key(
        'fk_waste_logs_food_item_id',
        'waste_logs', 'food_items',
        ['food_item_id'], ['id']
    )
```

**Update CRUD:**
```python
def create_waste_log(db: Session, data: dict, reported_by: int):
    from app.models.inventory import WasteLog, InventoryTransaction, InventoryItem
    from app.models.food import FoodItem  # Add this
    from datetime import datetime
    
    is_food = data.get("is_food_item", False)
    
    if is_food:
        # Handle food item waste
        food_item = db.query(FoodItem).filter(FoodItem.id == data["food_item_id"]).first()
        if not food_item:
            raise ValueError("Food item not found")
        
        log_number = generate_waste_log_number(db)
        waste_log = WasteLog(
            log_number=log_number,
            food_item_id=data["food_item_id"],
            is_food_item=True,
            location_id=data.get("location_id"),
            quantity=data["quantity"],
            unit=data["unit"],
            reason_code=data["reason_code"],
            action_taken=data.get("action_taken"),
            notes=data.get("notes"),
            reported_by=reported_by,
            waste_date=data.get("waste_date", datetime.utcnow()),
        )
        db.add(waste_log)
        # Note: Food items might not have stock tracking
        
    else:
        # Existing inventory item logic
        item = get_item_by_id(db, data["item_id"])
        if not item:
            raise ValueError("Item not found")
        
        if item.current_stock < data["quantity"]:
            raise ValueError(f"Insufficient stock")
        
        log_number = generate_waste_log_number(db)
        waste_log = WasteLog(
            log_number=log_number,
            item_id=data["item_id"],
            is_food_item=False,
            location_id=data.get("location_id"),
            quantity=data["quantity"],
            unit=data["unit"],
            reason_code=data["reason_code"],
            action_taken=data.get("action_taken"),
            notes=data.get("notes"),
            reported_by=reported_by,
            waste_date=data.get("waste_date", datetime.utcnow()),
        )
        db.add(waste_log)
        
        # Deduct stock
        item.current_stock -= data["quantity"]
        
        # Create transaction
        transaction = InventoryTransaction(
            item_id=data["item_id"],
            transaction_type="out",
            quantity=data["quantity"],
            unit_price=item.unit_price,
            total_amount=item.unit_price * data["quantity"] if item.unit_price else None,
            reference_number=log_number,
            notes=f"Waste/Spoilage: {data['reason_code']}",
            created_by=reported_by
        )
        db.add(transaction)
    
    db.commit()
    db.refresh(waste_log)
    return waste_log
```

**Update API Endpoint:**
```python
@router.post("/waste-logs", response_model=WasteLogOut)
def create_waste_log(
    item_id: Optional[int] = Form(None),
    food_item_id: Optional[int] = Form(None),
    is_food_item: bool = Form(False),
    location_id: Optional[int] = Form(None),
    quantity: float = Form(...),
    unit: str = Form(...),
    reason_code: str = Form(...),
    action_taken: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    waste_data = {
        "item_id": item_id,
        "food_item_id": food_item_id,
        "is_food_item": is_food_item,
        "location_id": int(location_id) if location_id else None,
        "quantity": quantity,
        "unit": unit,
        "reason_code": reason_code,
        "action_taken": action_taken,
        "notes": notes,
    }
    
    # ... rest of photo handling ...
    
    created = inventory_crud.create_waste_log(db, waste_data, reported_by=current_user.id)
    return created
```

---

## Summary

| Issue | Status | Action Required |
|-------|--------|----------------|
| Purchase Location | ✅ FIXED | None - Test in UI |
| Inventory Waste | ✅ WORKING | Check frontend refresh |
| Food Waste | ❌ BROKEN | Implement solution above |

### Immediate Next Steps

1. **Test Purchase Location**
   - Create new purchase with location
   - Verify it saves and displays

2. **Test Inventory Waste**
   - Log waste for inventory item
   - Check if `current_stock` decreases
   - Verify transaction appears

3. **Fix Food Waste**
   - Create migration for `food_item_id` and `is_food_item`
   - Update WasteLog model
   - Update CRUD function
   - Update API endpoint
   - Test with food item

### Files to Modify for Food Waste Fix

```
1. Create migration:
   alembic/versions/add_food_waste_support.py

2. Update model:
   app/models/inventory.py (WasteLog class)

3. Update CRUD:
   app/curd/inventory.py (create_waste_log function)

4. Update API:
   app/api/inventory.py (create_waste_log endpoint)

5. Update schema:
   app/schemas/inventory.py (WasteLogBase, WasteLogCreate)
```

---

## Conclusion

**Fixed Today:**
- ✅ Purchase destination location fully implemented

**Discovered:**
- ✅ Inventory waste IS working correctly
- ❌ Food waste needs model/schema updates

**Recommendation:**
Implement food waste support as outlined above to complete the waste management functionality.
