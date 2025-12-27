"""
Deduct check-in inventory for Room 102:
- 2x Coca Cola (already done)
- 4x Water (need to do)
"""
from app.database import SessionLocal
from app.models.inventory import InventoryItem, InventoryTransaction, LocationStock
from app.models.room import Room
from datetime import datetime


def deduct_checkin_inventory():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("CHECK-IN INVENTORY DEDUCTION - ROOM 102")
        print("=" * 70)
        print()
        
        # Items to deduct
        items_to_deduct = [
            {"name": "Coca Cola", "quantity": 2},
            {"name": "Water", "quantity": 4}
        ]
        
        room = db.query(Room).filter(Room.number == "102").first()
        if not room:
            print("❌ Room 102 not found")
            return
        
        print(f"🏠 Room: {room.number}")
        print()
        print("Items to deduct:")
        
        for item_data in items_to_deduct:
            print(f"  - {item_data['quantity']}x {item_data['name']}")
        print()
        
        # Check current status
        print("=" * 70)
        print("CURRENT STATUS")
        print("=" * 70)
        print()
        
        for item_data in items_to_deduct:
            item = db.query(InventoryItem).filter(
                InventoryItem.name.ilike(f"%{item_data['name']}%")
            ).first()
            
            if item:
                # Check existing transactions for this room
                existing_txns = db.query(InventoryTransaction).filter(
                    InventoryTransaction.item_id == item.id,
                    InventoryTransaction.reference_number.like("%CHECKIN-102%")
                ).all()
                
                total_deducted = sum(txn.quantity for txn in existing_txns if txn.transaction_type == "out")
                
                print(f"📦 {item.name}")
                print(f"   Current Stock: {item.current_stock} {item.unit}")
                print(f"   Already Deducted for Room 102: {total_deducted} {item.unit}")
                print(f"   Need to Deduct: {item_data['quantity']} {item.unit}")
                print(f"   Remaining to Deduct: {item_data['quantity'] - total_deducted} {item.unit}")
                print()
        
        print("=" * 70)
        confirm = input("Proceed with deduction? (yes/no): ").strip().lower()
        
        if confirm != "yes":
            print("❌ Operation cancelled")
            return
        
        print()
        print("=" * 70)
        print("PROCESSING DEDUCTIONS")
        print("=" * 70)
        print()
        
        # Process deductions
        for item_data in items_to_deduct:
            item = db.query(InventoryItem).filter(
                InventoryItem.name.ilike(f"%{item_data['name']}%")
            ).first()
            
            if not item:
                print(f"❌ {item_data['name']} not found, skipping")
                continue
            
            # Check existing transactions
            existing_txns = db.query(InventoryTransaction).filter(
                InventoryTransaction.item_id == item.id,
                InventoryTransaction.reference_number.like("%CHECKIN-102%")
            ).all()
            
            total_deducted = sum(txn.quantity for txn in existing_txns if txn.transaction_type == "out")
            remaining = item_data['quantity'] - total_deducted
            
            if remaining <= 0:
                print(f"✅ {item.name}: Already fully deducted ({total_deducted} {item.unit})")
                continue
            
            # Deduct remaining quantity
            old_stock = item.current_stock
            item.current_stock -= remaining
            
            # Create transaction
            transaction = InventoryTransaction(
                item_id=item.id,
                transaction_type="out",
                quantity=remaining,
                unit_price=item.unit_price,
                total_amount=item.unit_price * remaining if item.unit_price else None,
                reference_number=f"CHECKIN-102",
                department=item.category.parent_department if item.category else "Housekeeping",
                notes=f"Check-in inventory assignment - Room 102",
                created_by=None,
                created_at=datetime.utcnow()
            )
            db.add(transaction)
            
            # Update location stock
            location_stocks = db.query(LocationStock).filter(
                LocationStock.item_id == item.id
            ).all()
            
            if location_stocks:
                location_stock = location_stocks[0]
                old_loc_stock = location_stock.quantity
                location_stock.quantity -= remaining
                print(f"✅ {item.name}: Deducted {remaining} {item.unit}")
                print(f"   Global Stock: {old_stock} → {item.current_stock} {item.unit}")
                print(f"   Location Stock ({location_stock.location.name if location_stock.location else 'Unknown'}): {old_loc_stock} → {location_stock.quantity} {item.unit}")
            else:
                print(f"✅ {item.name}: Deducted {remaining} {item.unit}")
                print(f"   Global Stock: {old_stock} → {item.current_stock} {item.unit}")
            print()
        
        db.commit()
        
        print("=" * 70)
        print("✅ CHECK-IN INVENTORY DEDUCTION COMPLETE!")
        print("=" * 70)
        print()
        print("Summary:")
        print("  - 2x Coca Cola deducted for Room 102 ✅")
        print("  - 4x Water deducted for Room 102 ✅")
        print()
        print("Refresh your inventory page to see the updated stock.")
        print()
        
    except Exception as e:
        db.rollback()
        print()
        print("=" * 70)
        print("❌ ERROR")
        print("=" * 70)
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    deduct_checkin_inventory()
