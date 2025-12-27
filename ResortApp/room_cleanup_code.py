# Room cleanup helper - add this after checkout
# This code should be inserted after line 2518 in checkout.py

# 13.1. Return remaining consumables to warehouse (if any)
try:
    if room.inventory_location_id:
        from app.models.inventory import LocationStock, Location, InventoryTransaction, InventoryItem
        from sqlalchemy.orm import joinedload
        
        # Get consumable items still in room (exclude fixed assets)
        remaining = db.query(LocationStock).join(InventoryItem).options(
            joinedload(LocationStock.item)
        ).filter(
            LocationStock.location_id == room.inventory_location_id,
            LocationStock.quantity > 0,
            InventoryItem.is_fixed_asset == False
        ).all()
        
        if remaining:
            warehouse = db.query(Location).filter(Location.location_type == "WAREHOUSE").first()
            if warehouse:
                for item_stock in remaining:
                    qty = item_stock.quantity
                    item_name = item_stock.item.name if item_stock.item else f"Item #{item_stock.item_id}"
                    
                    # Add to warehouse
                    wh_stock = db.query(LocationStock).filter(
                        LocationStock.location_id == warehouse.id,
                        LocationStock.item_id == item_stock.item_id
                    ).first()
                    
                    if wh_stock:
                        wh_stock.quantity += qty
                        wh_stock.last_updated = datetime.utcnow()
                    else:
                        db.add(LocationStock(
                            location_id=warehouse.id,
                            item_id=item_stock.item_id,
                            quantity=qty,
                            last_updated=datetime.utcnow()
                        ))
                    
                    # Create transaction
                    db.add(InventoryTransaction(
                        item_id=item_stock.item_id,
                        transaction_type="transfer_out",
                        quantity=-qty,
                        location_id=room.inventory_location_id,
                        destination_location_id=warehouse.id,
                        transaction_date=datetime.utcnow(),
                        notes=f"Checkout cleanup - returned from Room {room.number}",
                        user_id=current_user.id if current_user else None
                    ))
                    
                    # Clear room stock
                    item_stock.quantity = 0
                    item_stock.last_updated = datetime.utcnow()
                    print(f"[CLEANUP] Returned {qty} x {item_name} from Room {room.number}")
except Exception as e:
    print(f"[WARNING] Cleanup failed for Room {room.number}: {e}")
    # Don't fail checkout if cleanup fails
