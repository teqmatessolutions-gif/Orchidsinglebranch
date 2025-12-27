# Fix: Automatic Stock Deduction at Check-In

## Problem

When items (Coca Cola, Water, etc.) are assigned to a room at check-in:
- ❌ Stock is NOT automatically deducted
- ❌ Only some items are deducted (inconsistent)
- ❌ Inventory counts become inaccurate

## Solution Overview

We need to ensure that whenever inventory items are assigned to a room (at check-in or any time), the stock is automatically deducted.

## Implementation Steps

### Step 1: Identify Where Items Are Assigned

The system likely has one of these mechanisms:

**Option A: Via Bookings API**
- When creating/updating a booking with extra inventory items
- File: `app/api/booking.py` or `app/curd/booking.py`

**Option B: Via Room Allocation**
- When assigning inventory to rooms directly
- File: `app/api/room.py` or similar

**Option C: Via Services**
- When assigning a service that includes inventory items
- File: `app/curd/service.py` (already has this logic)

### Step 2: Add Stock Deduction Logic

Wherever items are assigned to rooms, add this logic:

```python
def assign_inventory_to_room(db: Session, room_id: int, inventory_items: List[dict]):
    """
    Assign inventory items to a room and deduct stock
    
    Args:
        room_id: ID of the room
        inventory_items: List of dicts with 'item_id' and 'quantity'
    """
    from app.models.inventory import InventoryItem, InventoryTransaction, LocationStock
    from app.models.room import Room
    from datetime import datetime
    
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise ValueError(f"Room {room_id} not found")
    
    # Find main warehouse location
    main_location = db.query(Location).filter(
        (Location.location_type == "WAREHOUSE") | 
        (Location.location_type == "CENTRAL_WAREHOUSE") |
        (Location.is_inventory_point == True)
    ).first()
    
    for item_data in inventory_items:
        item_id = item_data['item_id']
        quantity = item_data['quantity']
        
        # Get inventory item
        item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if not item:
            print(f"[WARNING] Item {item_id} not found, skipping")
            continue
        
        # Check stock availability
        if item.current_stock < quantity:
            print(f"[WARNING] Insufficient stock for {item.name}. Available: {item.current_stock}, Required: {quantity}")
            # Continue anyway but log warning
        
        # Deduct from global stock
        old_stock = item.current_stock
        item.current_stock -= quantity
        print(f"[INFO] Deducted {quantity} {item.unit} of {item.name}. Stock: {old_stock} → {item.current_stock}")
        
        # Create inventory transaction
        transaction = InventoryTransaction(
            item_id=item_id,
            transaction_type="out",
            quantity=quantity,
            unit_price=item.unit_price,
            total_amount=item.unit_price * quantity if item.unit_price else None,
            reference_number=f"CHECKIN-{room.number}",
            department=item.category.parent_department if item.category else "Housekeeping",
            notes=f"Check-in inventory assignment - Room {room.number}",
            created_by=None,
            created_at=datetime.utcnow()
        )
        db.add(transaction)
        
        # Update location stock if main location exists
        if main_location:
            location_stock = db.query(LocationStock).filter(
                LocationStock.location_id == main_location.id,
                LocationStock.item_id == item_id
            ).first()
            
            if location_stock:
                old_loc_stock = location_stock.quantity
                location_stock.quantity -= quantity
                print(f"[INFO] Updated location stock for {main_location.name}: {old_loc_stock} → {location_stock.quantity}")
            else:
                print(f"[WARNING] No location stock found for {item.name} at {main_location.name}")
        
        # Create COGS journal entry
        try:
            db.flush()  # Get transaction ID
            from app.utils.accounting_helpers import create_consumption_journal_entry
            cogs_val = quantity * (item.unit_price or 0.0)
            if cogs_val > 0:
                create_consumption_journal_entry(
                    db=db,
                    consumption_id=transaction.id,
                    cogs_amount=cogs_val,
                    inventory_item_name=item.name,
                    created_by=None
                )
                print(f"[INFO] Created COGS journal entry for {item.name}")
        except Exception as je_error:
            print(f"[WARNING] Failed to create COGS journal entry: {je_error}")
    
    db.commit()
    print(f"[SUCCESS] Assigned {len(inventory_items)} items to Room {room.number}")
```

### Step 3: Integrate with Booking/Check-In Flow

Find where bookings are created/updated with inventory items and call the function:

```python
# In booking.py or wherever check-in happens
@router.post("/bookings/{booking_id}/assign-inventory")
def assign_inventory_at_checkin(
    booking_id: int,
    inventory_items: List[InventoryItemAssignment],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Get room from booking
    booking_room = db.query(BookingRoom).filter(
        BookingRoom.booking_id == booking_id
    ).first()
    
    if not booking_room:
        raise HTTPException(status_code=400, detail="No room assigned to booking")
    
    # Assign inventory and deduct stock
    assign_inventory_to_room(
        db=db,
        room_id=booking_room.room_id,
        inventory_items=[{
            'item_id': item.item_id,
            'quantity': item.quantity
        } for item in inventory_items]
    )
    
    return {"message": "Inventory assigned successfully"}
```

### Step 4: Add to Existing Check-In Code

If there's already code that assigns items at check-in, modify it to include stock deduction:

**Before (Broken):**
```python
# Just stores the assignment without deducting stock
for item in extra_inventory_items:
    # Save to database
    db.add(RoomInventoryAllocation(
        room_id=room_id,
        item_id=item.item_id,
        quantity=item.quantity
    ))
db.commit()
# ❌ Stock not deducted!
```

**After (Fixed):**
```python
# Stores assignment AND deducts stock
for item in extra_inventory_items:
    # Save to database
    db.add(RoomInventoryAllocation(
        room_id=room_id,
        item_id=item.item_id,
        quantity=item.quantity
    ))
    
    # ✅ Deduct stock
    inv_item = db.query(InventoryItem).filter(InventoryItem.id == item.item_id).first()
    if inv_item:
        inv_item.current_stock -= item.quantity
        
        # Create transaction
        transaction = InventoryTransaction(
            item_id=item.item_id,
            transaction_type="out",
            quantity=item.quantity,
            reference_number=f"CHECKIN-{room.number}",
            notes=f"Check-in assignment - Room {room.number}"
        )
        db.add(transaction)

db.commit()
```

## Testing

### Test Case 1: Single Item Assignment
1. Create a booking for Room 102
2. Assign 1x Coca Cola at check-in
3. **Verify**:
   - Coca Cola stock decreased by 1 ✅
   - Transaction created with type="out" ✅
   - Location stock updated ✅

### Test Case 2: Multiple Items Assignment
1. Create a booking for Room 103
2. Assign 2x Water, 1x Coca Cola at check-in
3. **Verify**:
   - Water stock decreased by 2 ✅
   - Coca Cola stock decreased by 1 ✅
   - 2 transactions created ✅

### Test Case 3: Insufficient Stock
1. Set Coca Cola stock to 0
2. Try to assign 1x Coca Cola at check-in
3. **Verify**:
   - Warning logged ✅
   - Assignment still happens (or fails gracefully) ✅
   - Stock goes negative (or assignment rejected) ✅

## Deployment

1. **Backup database** before deploying
2. **Test in development** environment first
3. **Deploy to production** during low-traffic period
4. **Monitor logs** for any errors
5. **Verify stock levels** after first few check-ins

## Rollback Plan

If issues occur:
1. Revert code changes
2. Manually adjust stock levels if needed
3. Investigate and fix before re-deploying

## Documentation

Update user documentation:
- Explain that stock is automatically deducted at check-in
- Show how to view transaction history
- Explain how to handle insufficient stock scenarios

## Summary

**Current State:** ❌ Stock not deducted when items assigned at check-in  
**Target State:** ✅ Stock automatically deducted with transaction logging  
**Files to Modify:** Booking/Room allocation code (exact file TBD)  
**Priority:** HIGH - Affects inventory accuracy  

Once implemented, every time items are assigned to a room at check-in, the stock will be automatically deducted and properly tracked.
