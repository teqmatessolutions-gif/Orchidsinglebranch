# BACKEND IMPLEMENTATION - All Critical Fixes

## This file contains the complete backend code to implement ALL critical fixes.
## Copy and paste the relevant sections into your backend files.

---

## File 1: app/api/inventory.py

### Replace the existing update_purchase endpoint (around line 582) with this:

```python
@router.put("/purchases/{purchase_id}", response_model=PurchaseMasterOut)
def update_purchase(
    purchase_id: int,
    purchase_update: PurchaseMasterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.inventory import InventoryItem, InventoryTransaction, LocationStock, Location
    from datetime import datetime
    
    # Get existing purchase
    purchase = inventory_crud.get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    old_status = purchase.status
    new_status = purchase_update.status if hasattr(purchase_update, 'status') else old_status
    
    # Update purchase fields
    updated = inventory_crud.update_purchase_master(db, purchase_id, purchase_update)
    if not updated:
        raise HTTPException(status_code=400, detail="Cannot update purchase")
    
    # CASE 1: Purchase is being RECEIVED (status changes to "received")
    if new_status == "received" and old_status != "received":
        for detail in updated.details:
            if not detail.item_id:
                continue
                
            item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
            if not item:
                continue
            
            # Calculate weighted average cost
            old_stock = item.current_stock or 0
            old_price = item.unit_price or 0
            old_value = old_stock * old_price
            
            new_stock = detail.quantity
            new_price = detail.unit_price
            new_value = new_stock * new_price
            
            total_stock = old_stock + new_stock
            total_value = old_value + new_value
            
            # Update item stock and cost
            item.current_stock = total_stock
            if total_stock > 0:
                item.unit_price = round(total_value / total_stock, 2)
            
            print(f"[PURCHASE RECEIVED] {item.name}: Stock {old_stock}→{total_stock}, Cost ₹{old_price}→₹{item.unit_price}")
            
            # Update location stock if destination specified
            if updated.destination_location_id:
                location_stock = db.query(LocationStock).filter(
                    LocationStock.location_id == updated.destination_location_id,
                    LocationStock.item_id == detail.item_id
                ).first()
                
                if location_stock:
                    location_stock.quantity += detail.quantity
                else:
                    location_stock = LocationStock(
                        location_id=updated.destination_location_id,
                        item_id=detail.item_id,
                        quantity=detail.quantity
                    )
                    db.add(location_stock)
                
                print(f"[LOCATION STOCK] Added {detail.quantity} to location {updated.destination_location_id}")
            
            # Create IN transaction
            transaction = InventoryTransaction(
                item_id=detail.item_id,
                transaction_type="in",
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                total_amount=detail.unit_price * detail.quantity,
                reference_number=updated.purchase_number,
                notes=f"Purchase received: {updated.purchase_number}. Cost updated to ₹{item.unit_price:.2f}",
                created_by=current_user.id
            )
            db.add(transaction)
    
    # CASE 2: Purchase is being CANCELLED (and it was previously received)
    elif new_status == "cancelled" and old_status == "received":
        for detail in updated.details:
            if not detail.item_id:
                continue
                
            item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
            if not item:
                continue
            
            # Reverse stock
            old_stock = item.current_stock
            new_stock = max(0, old_stock - detail.quantity)
            
            # Recalculate weighted average cost (remove cancelled purchase value)
            old_value = old_stock * item.unit_price
            cancelled_value = detail.quantity * detail.unit_price
            remaining_value = old_value - cancelled_value
            
            item.current_stock = new_stock
            if new_stock > 0:
                item.unit_price = round(remaining_value / new_stock, 2)
            
            print(f"[PURCHASE CANCELLED] {item.name}: Stock {old_stock}→{new_stock}, Cost recalculated to ₹{item.unit_price}")
            
            # Reverse location stock
            if updated.destination_location_id:
                location_stock = db.query(LocationStock).filter(
                    LocationStock.location_id == updated.destination_location_id,
                    LocationStock.item_id == detail.item_id
                ).first()
                
                if location_stock:
                    location_stock.quantity -= detail.quantity
                    if location_stock.quantity <= 0:
                        db.delete(location_stock)
                        print(f"[LOCATION STOCK] Removed all stock from location {updated.destination_location_id}")
                    else:
                        print(f"[LOCATION STOCK] Reduced by {detail.quantity} at location {updated.destination_location_id}")
            
            # Create reversal transaction
            transaction = InventoryTransaction(
                item_id=detail.item_id,
                transaction_type="out",
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                total_amount=detail.unit_price * detail.quantity,
                reference_number=updated.purchase_number,
                notes=f"Purchase cancelled - stock reversed: {updated.purchase_number}",
                created_by=current_user.id
            )
            db.add(transaction)
    
    db.commit()
    
    # Return full response
    return get_purchase(purchase_id, db, current_user)
```

---

## File 2: alembic/versions/add_food_waste_support.py

### Create this new migration file:

```python
"""Add food waste support

Revision ID: add_food_waste_support
Revises: add_purchase_location
Create Date: 2025-12-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_food_waste_support'
down_revision = 'add_purchase_location'
branch_labels = None
depends_on = None


def upgrade():
    # Add food_item_id and is_food_item columns
    op.add_column('waste_logs', 
        sa.Column('food_item_id', sa.Integer(), nullable=True)
    )
    op.add_column('waste_logs', 
        sa.Column('is_food_item', sa.Boolean(), default=False, nullable=False)
    )
    
    # Make item_id nullable (since we can have either item_id OR food_item_id)
    op.alter_column('waste_logs', 'item_id', nullable=True)
    
    # Add foreign key for food_item_id
    op.create_foreign_key(
        'fk_waste_logs_food_item_id',
        'waste_logs', 'food_items',
        ['food_item_id'], ['id']
    )


def downgrade():
    # Drop foreign key
    op.drop_constraint('fk_waste_logs_food_item_id', 'waste_logs', type_='foreignkey')
    
    # Drop columns
    op.drop_column('waste_logs', 'is_food_item')
    op.drop_column('waste_logs', 'food_item_id')
    
    # Make item_id required again
    op.alter_column('waste_logs', 'item_id', nullable=False)
```

---

## File 3: app/models/inventory.py

### Update the WasteLog model (around line 307):

```python
class WasteLog(Base):
    __tablename__ = "waste_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_number = Column(String, unique=True, nullable=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)  # Made nullable
    food_item_id = Column(Integer, ForeignKey("food_items.id"), nullable=True)  # NEW
    is_food_item = Column(Boolean, default=False, nullable=False)  # NEW
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    batch_number = Column(String, nullable=True)
    expiry_date = Column(Date, nullable=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    reason_code = Column(String, nullable=False)
    action_taken = Column(String, nullable=True)
    photo_path = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    waste_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    item = relationship("InventoryItem", foreign_keys=[item_id])
    food_item = relationship("FoodItem", foreign_keys=[food_item_id])  # NEW
    location = relationship("Location")
    reporter = relationship("User", foreign_keys=[reported_by])
```

---

## File 4: app/curd/inventory.py

### Update create_waste_log function (around line 601):

```python
def create_waste_log(db: Session, data: dict, reported_by: int):
    from app.models.inventory import WasteLog, InventoryTransaction, InventoryItem
    from app.models.food import FoodItem  # Add this import
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
            photo_path=data.get("photo_path"),
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
            raise ValueError(f"Insufficient stock for {item.name}. Available: {item.current_stock}, Reported: {data['quantity']}")
        
        log_number = generate_waste_log_number(db)
        waste_log = WasteLog(
            log_number=log_number,
            item_id=data["item_id"],
            is_food_item=False,
            location_id=data.get("location_id"),
            batch_number=data.get("batch_number"),
            expiry_date=data.get("expiry_date"),
            quantity=data["quantity"],
            unit=data["unit"],
            reason_code=data["reason_code"],
            action_taken=data.get("action_taken"),
            photo_path=data.get("photo_path"),
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
            notes=f"Waste/Spoilage: {data['reason_code']} - {data.get('notes', '')}",
            created_by=reported_by
        )
        db.add(transaction)
    
    db.commit()
    db.refresh(waste_log)
    return waste_log
```

---

## File 5: app/api/inventory.py - Waste Endpoint

### Update the waste log creation endpoint (around line 1074):

```python
@router.post("/waste-logs", response_model=WasteLogOut)
def create_waste_log(
    item_id: Optional[int] = Form(None),
    food_item_id: Optional[int] = Form(None),
    is_food_item: bool = Form(False),
    location_id: Optional[int] = Form(None),
    batch_number: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    quantity: float = Form(...),
    unit: str = Form(...),
    reason_code: str = Form(...),
    action_taken: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        from datetime import datetime as dt
        waste_data = {
            "item_id": item_id,
            "food_item_id": food_item_id,
            "is_food_item": is_food_item,
            "location_id": int(location_id) if location_id else None,
            "batch_number": batch_number,
            "expiry_date": dt.strptime(expiry_date, "%Y-%m-%d").date() if expiry_date else None,
            "quantity": quantity,
            "unit": unit,
            "reason_code": reason_code,
            "action_taken": action_taken if action_taken else None,
            "notes": notes,
        }
        
        # Handle photo upload
        if photo and photo.filename:
            WASTE_UPLOAD_DIR = "uploads/waste_logs"
            os.makedirs(WASTE_UPLOAD_DIR, exist_ok=True)
            filename = f"waste_{uuid.uuid4().hex}_{photo.filename}"
            file_path = os.path.join(WASTE_UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
            waste_data["photo_path"] = f"uploads/waste_logs/{filename}".replace("\\", "/")
        
        created = inventory_crud.create_waste_log(db, waste_data, reported_by=current_user.id)
        
        # Load relationships for response
        reporter = db.query(User).filter(User.id == created.reported_by).first()
        item = inventory_crud.get_item_by_id(db, created.item_id) if created.item_id else None
        food_item = db.query(FoodItem).filter(FoodItem.id == created.food_item_id).first() if created.food_item_id else None
        location = inventory_crud.get_location_by_id(db, created.location_id) if created.location_id else None
        
        return {
            **created.__dict__,
            "reporter_name": reporter.name if reporter else None,
            "item_name": item.name if item else (food_item.name if food_item else None),
            "location_name": location.name if location else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating waste log: {str(e)}")
```

---

## IMPLEMENTATION STEPS:

1. **Run migration for food waste:**
   ```bash
   cd c:\releasing\orchid\ResortApp
   python -m alembic upgrade head
   ```

2. **Backend will auto-reload** with the changes

3. **Test each fix:**
   - Create purchase, mark received → check stock increases
   - Cancel purchase → check stock decreases
   - Report waste for food item → should work now
   - Check item costs update with purchases

---

**All backend fixes are ready to implement!**
