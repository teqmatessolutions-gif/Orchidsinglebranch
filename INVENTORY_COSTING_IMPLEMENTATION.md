# Inventory Costing Implementation Guide

## Problem Statement
Currently, the inventory system uses a single `unit_price` for each item. When items are purchased at different times with different costs, and then issued/used, the system cannot accurately calculate the true cost of goods issued.

## Current Behavior
- Each inventory item has one `unit_price`
- When issuing items, cost = `unit_price × quantity`
- This doesn't reflect actual purchase costs or stock flow

## Required Solution: FIFO Costing

### What is FIFO?
**First In, First Out** - Items purchased first are issued/used first. This means:
- Stock is valued based on actual purchase costs
- Older inventory is consumed before newer inventory
- Cost of goods issued reflects the actual cost of the specific units being used

### Example Scenario

**Purchases:**
1. Jan 1: Buy 100 units @ ₹10 each = ₹1,000
2. Feb 1: Buy 100 units @ ₹12 each = ₹1,200
3. Mar 1: Buy 100 units @ ₹15 each = ₹1,500

**Total Stock:** 300 units, Total Value: ₹3,700

**Issue on Mar 15:** Issue 150 units

**FIFO Calculation:**
- First 100 units @ ₹10 = ₹1,000 (from Jan 1 batch)
- Next 50 units @ ₹12 = ₹600 (from Feb 1 batch)
- **Total Cost:** ₹1,600
- **Average Cost per Unit:** ₹1,600 / 150 = ₹10.67

**Remaining Stock:**
- 50 units @ ₹12 (from Feb 1)
- 100 units @ ₹15 (from Mar 1)
- **Total:** 150 units worth ₹2,100

---

## Backend Implementation Required

### 1. Database Schema Changes

#### New Table: `inventory_batches`
```sql
CREATE TABLE inventory_batches (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES inventory_items(id),
    location_id INTEGER REFERENCES locations(id),
    purchase_id INTEGER REFERENCES purchases(id),
    batch_number VARCHAR(50),
    purchase_date TIMESTAMP,
    unit_cost DECIMAL(10, 2),
    quantity_purchased DECIMAL(10, 2),
    quantity_remaining DECIMAL(10, 2),
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Update `issue_details` table
```sql
ALTER TABLE issue_details ADD COLUMN actual_cost DECIMAL(10, 2);
ALTER TABLE issue_details ADD COLUMN cost_calculation_method VARCHAR(20) DEFAULT 'FIFO';
```

### 2. API Endpoints to Create/Update

#### A. Create Batch on Purchase Receipt
**Endpoint:** `POST /inventory/purchases/{id}/receive`

When a purchase status changes to "received", create batch records:

```python
@router.post("/purchases/{purchase_id}/receive")
async def receive_purchase(
    purchase_id: int,
    destination_location_id: int,
    db: Session = Depends(get_db)
):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    
    for detail in purchase.details:
        # Create batch record
        batch = InventoryBatch(
            item_id=detail.item_id,
            location_id=destination_location_id,
            purchase_id=purchase_id,
            batch_number=f"BATCH-{purchase.purchase_number}-{detail.item_id}",
            purchase_date=purchase.purchase_date,
            unit_cost=detail.unit_price,  # Actual purchase cost
            quantity_purchased=detail.quantity,
            quantity_remaining=detail.quantity,
            expiry_date=detail.expiry_date
        )
        db.add(batch)
    
    purchase.status = "received"
    db.commit()
```

#### B. Calculate FIFO Cost on Issue
**Endpoint:** `POST /inventory/issues`

```python
def calculate_fifo_cost(item_id: int, location_id: int, quantity: float, db: Session):
    """
    Calculate cost using FIFO method
    Returns: (total_cost, batches_consumed)
    """
    # Get batches ordered by purchase date (oldest first)
    batches = db.query(InventoryBatch).filter(
        InventoryBatch.item_id == item_id,
        InventoryBatch.location_id == location_id,
        InventoryBatch.quantity_remaining > 0
    ).order_by(InventoryBatch.purchase_date).all()
    
    remaining_qty = quantity
    total_cost = 0
    batches_consumed = []
    
    for batch in batches:
        if remaining_qty <= 0:
            break
            
        # How much to take from this batch
        qty_from_batch = min(remaining_qty, batch.quantity_remaining)
        
        # Calculate cost
        cost_from_batch = qty_from_batch * batch.unit_cost
        total_cost += cost_from_batch
        
        # Update batch
        batch.quantity_remaining -= qty_from_batch
        
        # Track consumption
        batches_consumed.append({
            'batch_id': batch.id,
            'quantity': qty_from_batch,
            'unit_cost': batch.unit_cost,
            'cost': cost_from_batch
        })
        
        remaining_qty -= qty_from_batch
    
    if remaining_qty > 0:
        raise ValueError(f"Insufficient stock. Need {quantity}, available {quantity - remaining_qty}")
    
    return total_cost, batches_consumed

@router.post("/issues")
async def create_issue(issue_data: IssueCreate, db: Session = Depends(get_db)):
    issue = Issue(...)
    db.add(issue)
    
    for detail in issue_data.details:
        # Calculate FIFO cost
        total_cost, batches = calculate_fifo_cost(
            detail.item_id,
            issue_data.source_location_id,
            detail.issued_quantity,
            db
        )
        
        # Create issue detail with actual cost
        issue_detail = IssueDetail(
            issue_id=issue.id,
            item_id=detail.item_id,
            issued_quantity=detail.issued_quantity,
            actual_cost=total_cost,  # FIFO calculated cost
            cost_calculation_method='FIFO',
            batch_lot_number=detail.batch_lot_number,
            notes=f"FIFO cost from {len(batches)} batch(es)"
        )
        db.add(issue_detail)
    
    db.commit()
```

#### C. Get Batch Information
**Endpoint:** `GET /inventory/items/{item_id}/batches`

```python
@router.get("/items/{item_id}/batches")
async def get_item_batches(
    item_id: int,
    location_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(InventoryBatch).filter(
        InventoryBatch.item_id == item_id,
        InventoryBatch.quantity_remaining > 0
    )
    
    if location_id:
        query = query.filter(InventoryBatch.location_id == location_id)
    
    batches = query.order_by(InventoryBatch.purchase_date).all()
    
    return {
        'item_id': item_id,
        'total_quantity': sum(b.quantity_remaining for b in batches),
        'weighted_avg_cost': sum(b.quantity_remaining * b.unit_cost for b in batches) / sum(b.quantity_remaining for b in batches) if batches else 0,
        'batches': batches
    }
```

### 3. Handle Purchase Cancellation

When a purchase is cancelled, reverse the batch entries:

```python
@router.patch("/purchases/{purchase_id}/status")
async def update_purchase_status(
    purchase_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    
    if status == "cancelled" and purchase.status == "received":
        # Reverse batches
        batches = db.query(InventoryBatch).filter(
            InventoryBatch.purchase_id == purchase_id
        ).all()
        
        for batch in batches:
            if batch.quantity_remaining != batch.quantity_purchased:
                raise ValueError(f"Cannot cancel purchase - batch {batch.id} has been partially used")
            db.delete(batch)
    
    purchase.status = status
    db.commit()
```

---

## Frontend Implementation (Already Done)

### 1. Issue Form - Cost Display
✅ Added warning message about base cost vs FIFO cost
✅ Changed column header to "Cost (Base)" to indicate it's not batch-specific

### 2. What Frontend Should Do (Future)

When backend is ready:

#### A. Show Batch Information on Issue
```jsx
// Fetch available batches when item is selected
const batches = await api.get(`/inventory/items/${itemId}/batches?location_id=${sourceLocationId}`);

// Display batch info
<div className="text-xs text-gray-600 mt-1">
  Available: {batches.total_quantity} {item.unit}
  <br />
  Avg Cost: ₹{batches.weighted_avg_cost.toFixed(2)}
  <br />
  {batches.batches.length} batch(es)
</div>
```

#### B. Show Cost Breakdown in Issue Details
```jsx
// In IssueDetailsModal
{detail.cost_calculation_method === 'FIFO' && (
  <td className="px-3 py-2 text-sm">
    ₹{detail.actual_cost.toFixed(2)}
    <span className="text-xs text-gray-500 ml-1">(FIFO)</span>
  </td>
)}
```

---

## Testing Checklist

### Scenario 1: Basic FIFO
1. Purchase 100 units @ ₹10
2. Purchase 100 units @ ₹15
3. Issue 150 units
4. **Expected Cost:** (100 × ₹10) + (50 × ₹15) = ₹1,750
5. **Remaining:** 50 units @ ₹15

### Scenario 2: Multiple Locations
1. Purchase to Location A: 100 units @ ₹10
2. Purchase to Location B: 100 units @ ₹12
3. Issue from Location A: 50 units
4. **Expected Cost:** 50 × ₹10 = ₹500
5. Location B stock should be unaffected

### Scenario 3: Insufficient Stock
1. Purchase 50 units @ ₹10
2. Try to issue 100 units
3. **Expected:** Error - "Insufficient stock"

### Scenario 4: Purchase Cancellation
1. Purchase 100 units @ ₹10 (received)
2. Issue 30 units
3. Try to cancel purchase
4. **Expected:** Error - "Cannot cancel, batch partially used"

---

## Alternative: Weighted Average Cost

If FIFO is too complex, use **Weighted Average Cost**:

```python
def calculate_weighted_avg_cost(item_id: int, location_id: int):
    batches = db.query(InventoryBatch).filter(
        InventoryBatch.item_id == item_id,
        InventoryBatch.location_id == location_id,
        InventoryBatch.quantity_remaining > 0
    ).all()
    
    total_qty = sum(b.quantity_remaining for b in batches)
    total_value = sum(b.quantity_remaining * b.unit_cost for b in batches)
    
    return total_value / total_qty if total_qty > 0 else 0
```

**Pros:**
- Simpler to implement
- No need to track which batch is consumed
- Good for fungible items

**Cons:**
- Less accurate than FIFO
- Doesn't reflect actual stock flow

---

## Summary

**Current Status:**
- ✅ Frontend shows warning about cost calculation
- ❌ Backend doesn't track batches
- ❌ Backend doesn't calculate FIFO cost

**Next Steps:**
1. Implement `inventory_batches` table
2. Create batches on purchase receipt
3. Implement FIFO cost calculation
4. Update issue creation to use FIFO
5. Update frontend to show batch info (when backend ready)

**Priority:** HIGH - This affects financial accuracy and inventory valuation
