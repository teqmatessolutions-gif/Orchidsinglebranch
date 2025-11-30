"""
Helper functions for comprehensive checkout system
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, time
from typing import List, Dict, Optional
from app.models.inventory import InventoryItem, InventoryTransaction, Location
from app.models.room import Room
from app.models.checkout import CheckoutVerification, CheckoutPayment
from app.schemas.checkout import ConsumableAuditItem, AssetDamageItem, RoomVerificationData, SplitPaymentItem


def calculate_late_checkout_fee(booking_checkout_date: date, actual_checkout_time: Optional[datetime], 
                                room_rate: float, late_checkout_threshold_hour: int = 12) -> float:
    """
    Calculate late checkout fee (50% of room rate if checkout after threshold hour)
    """
    if not actual_checkout_time:
        return 0.0
    
    actual_date = actual_checkout_time.date()
    actual_hour = actual_checkout_time.hour
    
    # If checkout is on a different day than booking checkout date, it's definitely late
    if actual_date > booking_checkout_date:
        return room_rate * 0.5
    
    # If same day but after threshold hour, charge late fee
    if actual_date == booking_checkout_date and actual_hour >= late_checkout_threshold_hour:
        return room_rate * 0.5
    
    return 0.0


def process_consumables_audit(db: Session, room_id: int, consumables: List[ConsumableAuditItem]) -> Dict:
    """
    Process consumables audit and calculate charges
    Returns: {total_charge: float, items_charged: List[Dict]}
    """
    total_charge = 0.0
    items_charged = []
    
    for item in consumables:
        # Get inventory item to verify
        inv_item = db.query(InventoryItem).filter(InventoryItem.id == item.item_id).first()
        if not inv_item:
            continue
        
        # Calculate charge for items consumed beyond complimentary limit
        excess_quantity = max(0, item.actual_consumed - item.complimentary_limit)
        if excess_quantity > 0:
            charge = excess_quantity * item.charge_per_unit
            total_charge += charge
            items_charged.append({
                "item_id": item.item_id,
                "item_name": item.item_name,
                "complimentary_limit": item.complimentary_limit,
                "actual_consumed": item.actual_consumed,
                "excess_quantity": excess_quantity,
                "charge_per_unit": item.charge_per_unit,
                "total_charge": charge
            })
    
    return {
        "total_charge": total_charge,
        "items_charged": items_charged
    }


def process_asset_damage_check(asset_damages: List[AssetDamageItem]) -> Dict:
    """
    Process asset damage check and calculate replacement costs
    Returns: {total_charge: float, damages: List[Dict]}
    """
    total_charge = sum(damage.replacement_cost for damage in asset_damages)
    damages = [
        {
            "item_name": damage.item_name,
            "replacement_cost": damage.replacement_cost,
            "notes": damage.notes
        }
        for damage in asset_damages
    ]
    
    return {
        "total_charge": total_charge,
        "damages": damages
    }


def deduct_room_consumables(db: Session, room_id: int, consumables: List[ConsumableAuditItem], 
                           checkout_id: int, created_by: Optional[int] = None):
    """
    Deduct consumed items from room inventory
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room or not room.inventory_location_id:
        return
    
    location = db.query(Location).filter(Location.id == room.inventory_location_id).first()
    if not location:
        return
    
    for item in consumables:
        inv_item = db.query(InventoryItem).filter(InventoryItem.id == item.item_id).first()
        if not inv_item:
            continue
        
        # Deduct actual consumed quantity from inventory
        quantity_to_deduct = item.actual_consumed
        if inv_item.current_stock >= quantity_to_deduct:
            inv_item.current_stock -= quantity_to_deduct
            
            # Create inventory transaction
            transaction = InventoryTransaction(
                item_id=item.item_id,
                transaction_type="out",
                quantity=quantity_to_deduct,
                unit_price=inv_item.unit_price or 0.0,
                total_amount=(inv_item.unit_price or 0.0) * quantity_to_deduct,
                reference_number=f"CHECKOUT-{checkout_id}",
                notes=f"Checkout consumption - Room {room.number if room else 'N/A'}",
                created_by=created_by
            )
            db.add(transaction)


def trigger_linen_cycle(db: Session, room_id: int, checkout_id: int):
    """
    Move bed sheets and towels to laundry queue (dirty status)
    Logic: Find all linen items in room inventory and mark them as dirty
    """
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room or not room.inventory_location_id:
        return
    
    # Find linen items (items with track_laundry_cycle = True) in room location
    linen_items = db.query(InventoryItem).filter(
        InventoryItem.track_laundry_cycle == True
    ).all()
    
    # For each linen item, create a transaction marking it as dirty
    # In a full implementation, you'd have a LaundryQueue table
    # For now, we'll create inventory transactions with a special reference
    for item in linen_items:
        # Create transaction to track linen movement to laundry
        transaction = InventoryTransaction(
            item_id=item.id,
            transaction_type="out",  # Out from room
            quantity=1.0,  # Assuming 1 set per room
            unit_price=0.0,  # No cost, just tracking
            reference_number=f"LAUNDRY-{checkout_id}",
            notes=f"Linen cycle triggered - Room {room.number if room else 'N/A'} - Moved to laundry queue",
            created_by=None
        )
        db.add(transaction)


def create_checkout_verification(db: Session, checkout_id: int, room_verification: RoomVerificationData, room_id: Optional[int] = None) -> CheckoutVerification:
    """
    Create checkout verification record for a room
    """
    # Get room_id if not provided
    if not room_id:
        from app.models.room import Room
        room = db.query(Room).filter(Room.number == room_verification.room_number).first()
        room_id = room.id if room else None
    
    # Process consumables audit
    consumables_audit = process_consumables_audit(
        db, 
        room_id=room_id or 0,  # Use room_id if available
        consumables=room_verification.consumables
    )
    
    # Process asset damages
    asset_damage = process_asset_damage_check(room_verification.asset_damages)
    
    # Calculate key card fee (if not returned)
    key_card_fee = 0.0 if room_verification.key_card_returned else 50.0  # Default fee
    
    verification = CheckoutVerification(
        checkout_id=checkout_id,
        room_number=room_verification.room_number,
        housekeeping_status=room_verification.housekeeping_status,
        housekeeping_notes=room_verification.housekeeping_notes,
        consumables_audit_data={
            item.item_id: {
                "actual": item.actual_consumed,
                "limit": item.complimentary_limit,
                "charge": item.total_charge
            }
            for item in room_verification.consumables
        },
        consumables_total_charge=consumables_audit["total_charge"],
        asset_damages=[
            {
                "item_name": d.item_name,
                "replacement_cost": d.replacement_cost,
                "notes": d.notes
            }
            for d in room_verification.asset_damages
        ],
        asset_damage_total=asset_damage["total_charge"],
        key_card_returned=room_verification.key_card_returned,
        key_card_fee=key_card_fee
    )
    
    db.add(verification)
    return verification


def process_split_payments(db: Session, checkout_id: int, split_payments: List[SplitPaymentItem]) -> List[CheckoutPayment]:
    """
    Create payment records for split payments
    """
    payment_records = []
    for payment in split_payments:
        payment_record = CheckoutPayment(
            checkout_id=checkout_id,
            payment_method=payment.payment_method,
            amount=payment.amount,
            transaction_id=payment.transaction_id,
            notes=payment.notes
        )
        db.add(payment_record)
        payment_records.append(payment_record)
    
    return payment_records


def generate_invoice_number(db: Session) -> str:
    """
    Generate unique invoice number (e.g., INV-2025-001234)
    """
    today = date.today()
    year = today.year
    month = today.month
    
    # Get count of invoices this month
    from app.models.checkout import Checkout
    count = db.query(Checkout).filter(
        func.extract('year', Checkout.created_at) == year,
        func.extract('month', Checkout.created_at) == month
    ).count()
    
    invoice_number = f"INV-{year}-{str(count + 1).zfill(6)}"
    return invoice_number


def calculate_gst_breakdown(room_charges: float, food_charges: float, package_charges: float) -> Dict:
    """
    Calculate GST breakdown with dynamic rates
    Room: 12% if < 7500, 18% if >= 7500
    Food: 5% or 18% (configurable)
    Package: Same as room
    """
    # Room GST
    if room_charges > 0:
        if room_charges < 7500:
            room_gst = room_charges * 0.12
        else:
            room_gst = room_charges * 0.18
    else:
        room_gst = 0.0
    
    # Package GST (same as room)
    if package_charges > 0:
        if package_charges < 7500:
            package_gst = package_charges * 0.12
        else:
            package_gst = package_charges * 0.18
    else:
        package_gst = 0.0
    
    # Food GST (5% typically, or 18% if composite supply)
    food_gst = food_charges * 0.05  # Default 5%, can be made configurable
    
    total_gst = room_gst + food_gst + package_gst
    
    return {
        "room_gst": room_gst,
        "food_gst": food_gst,
        "package_gst": package_gst,
        "total_gst": total_gst
    }

