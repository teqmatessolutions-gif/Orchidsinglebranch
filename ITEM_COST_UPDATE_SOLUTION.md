# Issue 7: Item Cost Not Updating with Purchase Cost

## Problem
When a purchase is received, the item's `unit_price` should update to reflect the new purchase cost. Currently, the item cost remains static even after new purchases at different prices.

## Impact
- Inventory valuation is incorrect
- Cost calculations in issues/waste are outdated
- Cannot track price changes over time

## Solution Options

### Option 1: Latest Purchase Price (Simplest)
Update item cost to match the most recent purchase price.

**Pros:**
- Simple to implement
- Reflects current market price
- Easy to understand

**Cons:**
- Doesn't account for existing stock at different prices
- Can cause sudden valuation changes

**Implementation:**
```python
# In purchase status update (when status changes to "received")
for detail in purchase.details:
    item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
    
    # Update stock
    item.current_stock += detail.quantity
    
    # Update cost to latest purchase price
    item.unit_price = detail.unit_price
    
    # Optional: Track price history
    price_history = ItemPriceHistory(
        item_id=item.id,
        old_price=item.unit_price,
        new_price=detail.unit_price,
        purchase_id=purchase.id,
        changed_at=datetime.utcnow()
    )
    db.add(price_history)
```

---

### Option 2: Weighted Average Cost (Recommended)
Calculate weighted average based on existing stock and new purchase.

**Pros:**
- More accurate valuation
- Smooths out price fluctuations
- Industry standard (AVCO method)

**Cons:**
- Slightly more complex
- Requires calculation

**Formula:**
```
New Average Cost = (Old Stock Value + New Purchase Value) / (Old Stock + New Stock)

Where:
- Old Stock Value = current_stock × unit_price
- New Purchase Value = purchase_quantity × purchase_unit_price
```

**Implementation:**
```python
# In purchase status update (when status changes to "received")
for detail in purchase.details:
    item = db.query(InventoryItem).filter(InventoryItem.id == detail.item_id).first()
    
    # Calculate weighted average cost
    old_stock = item.current_stock
    old_price = item.unit_price or 0
    old_value = old_stock * old_price
    
    new_stock = detail.quantity
    new_price = detail.unit_price
    new_value = new_stock * new_price
    
    total_stock = old_stock + new_stock
    total_value = old_value + new_value
    
    # Update item with new average cost
    if total_stock > 0:
        item.unit_price = total_value / total_stock
    
    item.current_stock = total_stock
    
    # Optional: Log the cost change
    if old_price != item.unit_price:
        cost_change_log = ItemCostChangeLog(
            item_id=item.id,
            old_cost=old_price,
            new_cost=item.unit_price,
            old_stock=old_stock,
            new_stock=new_stock,
            purchase_reference=purchase.purchase_number,
            changed_at=datetime.utcnow()
        )
        db.add(cost_change_log)
```

---

### Option 3: FIFO (First In, First Out)
Track each batch separately with its own cost.

**Pros:**
- Most accurate for perishable items
- Tracks actual costs per batch
- Better for expiry management

**Cons:**
- Complex implementation
- Requires batch tracking
- More database records

**Note:** This is documented in detail in `INVENTORY_COSTING_IMPLEMENTATION.md`

---

## Recommended Implementation

**Use Weighted Average Cost (Option 2)** because:
1. Balances accuracy and simplicity
2. Industry standard
3. Works well for most inventory types
4. Doesn't require batch tracking

---

## Complete Backend Code

### File: `app/api/inventory.py`

```python
@router.patch("/purchases/{purchase_id}")
def update_purchase_status(
    purchase_id: int,
    status_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    purchase = db.query(PurchaseMaster).filter(
        PurchaseMaster.id == purchase_id
    ).first()
    
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    old_status = purchase.status
    new_status = status_update.get("status")
    
    # CASE 1: Receiving purchase - Add stock and update costs
    if new_status == "received" and old_status != "received":
        for detail in purchase.details:
            item = db.query(InventoryItem).filter(
                InventoryItem.id == detail.item_id
            ).first()
            
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
                notes=f"Purchase received: {purchase.purchase_number}. "
                      f"Cost updated from ₹{old_price:.2f} to ₹{item.unit_price:.2f}",
                created_by=current_user.id
            )
            db.add(transaction)
    
    # CASE 2: Cancelling received purchase - Reverse stock and recalculate cost
    elif new_status == "cancelled" and old_status == "received":
        for detail in purchase.details:
            item = db.query(InventoryItem).filter(
                InventoryItem.id == detail.item_id
            ).first()
            
            if not item:
                continue
            
            # Reverse stock
            old_stock = item.current_stock
            new_stock = old_stock - detail.quantity
            
            # Recalculate weighted average cost
            # Remove the cancelled purchase value from total
            old_value = old_stock * item.unit_price
            cancelled_value = detail.quantity * detail.unit_price
            remaining_value = old_value - cancelled_value
            
            item.current_stock = max(0, new_stock)
            if new_stock > 0:
                item.unit_price = round(remaining_value / new_stock, 2)
            
            # Reverse location stock
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
    
    # Update purchase status
    purchase.status = new_status
    db.commit()
    db.refresh(purchase)
    
    return purchase
```

---

## Example Calculation

### Scenario:
1. **Initial State:**
   - Item: Rice
   - Stock: 100 kg
   - Cost: ₹50/kg
   - Total Value: ₹5,000

2. **New Purchase:**
   - Quantity: 50 kg
   - Cost: ₹60/kg
   - Purchase Value: ₹3,000

3. **After Receiving:**
   ```
   New Average Cost = (5,000 + 3,000) / (100 + 50)
                    = 8,000 / 150
                    = ₹53.33/kg
   
   New Stock: 150 kg
   New Cost: ₹53.33/kg
   Total Value: ₹8,000
   ```

4. **If Purchase Cancelled:**
   ```
   Remaining Value = 8,000 - 3,000 = 5,000
   Remaining Stock = 150 - 50 = 100 kg
   
   Recalculated Cost = 5,000 / 100 = ₹50/kg
   
   (Back to original state)
   ```

---

## Testing Checklist

### Test 1: New Purchase Updates Cost
- [ ] Create item with stock 100, cost ₹50
- [ ] Create purchase: 50 units at ₹60
- [ ] Mark as received
- [ ] Verify item cost updated to ₹53.33
- [ ] Verify stock is 150

### Test 2: Multiple Purchases
- [ ] Start with 100 @ ₹50
- [ ] Purchase 1: 50 @ ₹60 (should be ₹53.33)
- [ ] Purchase 2: 25 @ ₹70 (should be ₹56.67)
- [ ] Verify progressive cost updates

### Test 3: Cancelled Purchase Reverses Cost
- [ ] Have stock 150 @ ₹53.33
- [ ] Cancel purchase of 50 @ ₹60
- [ ] Verify cost reverts to ₹50
- [ ] Verify stock is 100

### Test 4: Zero Stock Purchase
- [ ] Item with 0 stock, cost ₹0
- [ ] Purchase 100 @ ₹50
- [ ] Verify cost becomes ₹50
- [ ] Verify stock is 100

---

## Additional Enhancements

### 1. Price Change Notification
```python
# After updating cost
if abs(old_price - item.unit_price) > (old_price * 0.1):  # 10% change
    notification = Notification(
        user_id=current_user.id,
        title=f"Significant Price Change: {item.name}",
        message=f"Cost changed from ₹{old_price:.2f} to ₹{item.unit_price:.2f}",
        type="warning"
    )
    db.add(notification)
```

### 2. Cost History Tracking
```python
# Optional: Create price history table
class ItemPriceHistory(Base):
    __tablename__ = "item_price_history"
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"))
    old_price = Column(Numeric(10, 2))
    new_price = Column(Numeric(10, 2))
    old_stock = Column(Float)
    new_stock = Column(Float)
    purchase_reference = Column(String)
    changed_at = Column(DateTime, default=datetime.utcnow)
```

---

## Summary

**Issue:** Item costs don't update with new purchases  
**Solution:** Implement weighted average costing  
**Priority:** 🔴 CRITICAL  
**Effort:** MEDIUM (1-2 hours)  
**Impact:** HIGH - Affects all inventory valuations

**This should be implemented together with the cancelled purchase fix for consistency.**
