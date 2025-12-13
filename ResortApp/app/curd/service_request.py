from sqlalchemy.orm import Session, joinedload
from app.models.service_request import ServiceRequest
from app.models.foodorder import FoodOrder
from app.models.room import Room
from app.models.employee import Employee
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestUpdate
from typing import List, Optional
from datetime import datetime
# Notification system removed

def create_service_request(db: Session, request_data: ServiceRequestCreate):
    request = ServiceRequest(
        food_order_id=request_data.food_order_id,
        room_id=request_data.room_id,
        employee_id=request_data.employee_id,
        request_type=request_data.request_type,
        description=request_data.description,
        status="pending"
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    
    # Notification system removed for performance
    
    return request

def create_cleaning_service_request(db: Session, room_id: int, room_number: str, guest_name: str = None):
    """
    Create a cleaning service request after checkout.
    This is automatically triggered when a room is checked out.
    """
    request = ServiceRequest(
        food_order_id=None,  # Cleaning requests don't have food orders
        room_id=room_id,
        employee_id=None,  # Will be assigned later
        request_type="cleaning",
        description=f"Room cleaning required after checkout - Room {room_number}" + (f" (Guest: {guest_name})" if guest_name else ""),
        status="pending"
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    
    # Notification system removed for performance
    
    return request

def create_refill_service_request(db: Session, room_id: int, room_number: str, guest_name: str = None, checkout_id: int = None):
    """
    Create a refill service request after checkout.
    This is automatically triggered when a room is checked out to replenish inventory items.
    Refill requirements are calculated from the checkout consumables audit.
    """
    import json
    refill_items = []
    
    # Get refill requirements from checkout verification if checkout_id is provided
    if checkout_id:
        from app.models.checkout import CheckoutVerification
        from app.models.inventory import InventoryItem
        
        # Get the checkout verification for this room
        verification = db.query(CheckoutVerification).filter(
            CheckoutVerification.checkout_id == checkout_id,
            CheckoutVerification.room_number == room_number
        ).first()
        
        if verification and verification.consumables_audit_data:
            # Extract consumables data and calculate refill requirements
            consumables_data = verification.consumables_audit_data
            
            for item_id_str, item_data in consumables_data.items():
                try:
                    item_id = int(item_id_str)
                    actual_consumed = item_data.get("actual", 0)
                    
                    # Get inventory item details
                    inv_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
                    if inv_item and actual_consumed > 0:
                        # What was consumed needs to be refilled
                        refill_items.append({
                            "item_id": item_id,
                            "item_name": inv_item.name,
                            "item_code": inv_item.item_code,
                            "quantity_to_refill": actual_consumed,
                            "unit": inv_item.unit or "pcs"
                        })
                except (ValueError, KeyError):
                    continue
    
    # Build description with refill requirements
    description_parts = [f"Room inventory refill required after checkout - Room {room_number}"]
    if guest_name:
        description_parts.append(f"Previous Guest: {guest_name}")
    
    if refill_items:
        description_parts.append("Refill Requirements:")
        for item in refill_items:
            description_parts.append(f"- {item['item_name']}: {item['quantity_to_refill']} {item['unit']}")
    else:
        description_parts.append("Standard inventory refill required")
    
    request = ServiceRequest(
        food_order_id=None,  # Refill requests don't have food orders
        room_id=room_id,
        employee_id=None,  # Will be assigned later
        request_type="refill",
        description=" | ".join(description_parts),
        refill_data=json.dumps(refill_items) if refill_items else None,  # Store as JSON
        status="pending"
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

def create_return_items_service_request(db: Session, room_id: int, room_number: str, guest_name: str = None, checkout_id: int = None):
    """
    Create a return items service request after checkout.
    This tells staff to collect unused items from the room and return them to warehouse.
    """
    import json
    return_items = []
    
    # Get items that need to be returned from checkout verification
    if checkout_id:
        from app.models.checkout import CheckoutVerification
        from app.models.inventory import InventoryItem, LocationStock
        
        # Get the checkout verification for this room
        verification = db.query(CheckoutVerification).filter(
            CheckoutVerification.checkout_id == checkout_id,
            CheckoutVerification.room_number == room_number
        ).first()
        
        if verification and verification.consumables_audit_data:
            # Extract consumables data and find unused items
            consumables_data = verification.consumables_audit_data
            
            for item_id_str, item_data in consumables_data.items():
                try:
                    item_id = int(item_id_str)
                    issued_qty = item_data.get("issued", 0)
                    actual_consumed = item_data.get("actual", 0)
                    returned_qty = issued_qty - actual_consumed  # Items not consumed = returned
                    
                    if returned_qty > 0:
                        # Get inventory item details
                        inv_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
                        if inv_item:
                            return_items.append({
                                "item_id": item_id,
                                "item_name": inv_item.name,
                                "item_code": inv_item.item_code,
                                "quantity_to_return": returned_qty,
                                "unit": inv_item.unit or "pcs"
                            })
                except (ValueError, KeyError):
                    continue
    
    # Only create service request if there are items to return
    if not return_items:
        return None
    
    # Build description with return requirements
    description_parts = [f"Collect and return unused items to warehouse - Room {room_number}"]
    if guest_name:
        description_parts.append(f"Previous Guest: {guest_name}")
    
    description_parts.append("Items to Return:")
    for item in return_items:
        description_parts.append(f"- {item['item_name']}: {item['quantity_to_return']} {item['unit']}")
    
    request = ServiceRequest(
        food_order_id=None,
        room_id=room_id,
        employee_id=None,  # Will be assigned later
        request_type="return_items",
        description=" | ".join(description_parts),
        refill_data=json.dumps(return_items),  # Store return items as JSON
        status="pending"
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request

def get_service_requests(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None):
    query = db.query(ServiceRequest).options(
        joinedload(ServiceRequest.food_order),
        joinedload(ServiceRequest.room),
        joinedload(ServiceRequest.employee)
    )
    
    if status:
        query = query.filter(ServiceRequest.status == status)
    
    requests = query.offset(skip).limit(limit).all()
    
    # Enrich with additional data
    for req in requests:
        if req.food_order:
            req.food_order_amount = req.food_order.amount
            req.food_order_status = req.food_order.status
        if req.room:
            req.room_number = req.room.number
        # Always set employee_name, even if None
        req.employee_name = req.employee.name if req.employee else None
    
    return requests

def get_service_request(db: Session, request_id: int):
    request = db.query(ServiceRequest).options(
        joinedload(ServiceRequest.food_order),
        joinedload(ServiceRequest.room),
        joinedload(ServiceRequest.employee)
    ).filter(ServiceRequest.id == request_id).first()
    
    if request:
        if request.food_order:
            request.food_order_amount = request.food_order.amount
            request.food_order_status = request.food_order.status
        if request.room:
            request.room_number = request.room.number
        # Always set employee_name, even if None
        request.employee_name = request.employee.name if request.employee else None
    
    return request

def update_service_request(db: Session, request_id: int, update_data: ServiceRequestUpdate):
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        return None
    
    old_status = request.status
    
    # Track if status is changing to completed
    is_completing = False
    if update_data.status is not None and update_data.status == "completed" and request.status != "completed":
        is_completing = True
    
    if update_data.status is not None:
        request.status = update_data.status
        if update_data.status == "completed":
            request.completed_at = datetime.utcnow()
            
            # If this is a delivery request with a food order, update the food order status
            if request.food_order_id and is_completing:
                food_order = db.query(FoodOrder).filter(FoodOrder.id == request.food_order_id).first()
                if food_order:
                    # Mark food order as completed
                    food_order.status = "completed"
                    
                    # Use billing_status from update_data if provided, otherwise default to unpaid
                    if update_data.billing_status:
                        food_order.billing_status = update_data.billing_status
                    elif food_order.billing_status != "paid":
                        food_order.billing_status = "unpaid"
                    
                    print(f"[INFO] Food order {food_order.id} marked as completed (billing: {food_order.billing_status}) due to delivery service completion")

            # Sync with AssignedService: Heuristic to auto-complete duplicate manual assignments
            if is_completing:
                try:
                    from app.models.service import AssignedService, Service
                    from app.curd.service import update_assigned_service_status
                    from app.schemas.service import AssignedServiceUpdate

                    target_employee_id = update_data.employee_id or request.employee_id
                    
                    if target_employee_id and request.room_id:
                        # Use nested transaction to isolate failures
                        try:
                            with db.begin_nested():
                                # Find pending assigned services for this room/employee
                                query = db.query(AssignedService).join(Service).filter(
                                    AssignedService.room_id == request.room_id,
                                    AssignedService.employee_id == target_employee_id,
                                    AssignedService.status.notin_(['completed', 'cancelled', 'rejected'])
                                )
                                
                                # Apply name filter based on request type to avoid false positives
                                if request.request_type == 'delivery':
                                    query = query.filter(Service.name.ilike('%food%') | Service.name.ilike('%delivery%'))
                                elif request.request_type == 'cleaning':
                                    query = query.filter(Service.name.ilike('%clean%') | Service.name.ilike('%housekeep%') | Service.name.ilike('%room%'))
                                elif request.request_type == 'refill':
                                    query = query.filter(Service.name.ilike('%refill%'))
                                
                                # Only auto-complete services assigned within the last 48 hours to be safe
                                matching_services = query.all()
                                
                                for svc in matching_services:
                                    # Verify timestamp safely
                                    assigned_time = svc.assigned_at or datetime.utcnow()
                                    time_diff = datetime.utcnow() - assigned_time
                                    if time_diff.total_seconds() < 172800: # 48 hours
                                        print(f"[INFO] Auto-completing linked AssignedService {svc.id} ({svc.service.name}) matching ServiceRequest {request.id}")
                                        update_assigned_service_status(db, svc.id, AssignedServiceUpdate(status='completed'), commit=False)
                        except Exception as nested_error:
                            print(f"[WARNING] Nested transaction failed during AssignedService sync: {nested_error}")
                            import traceback
                            print(traceback.format_exc())
                            # Don't rollback - continue with main update even if sync fails
                except Exception as sync_error:
                    print(f"[WARNING] Failed to sync AssignedService status: {sync_error}")
                    import traceback
                    print(traceback.format_exc())
                    # Don't rollback - continue with main update even if sync fails
    
    if update_data.employee_id is not None:
        request.employee_id = update_data.employee_id
    if update_data.description is not None:
        request.description = update_data.description
    
    db.commit()
    db.refresh(request)
    
    
    # Notification system removed for performance
    
    return request

def delete_service_request(db: Session, request_id: int):
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if request:
        db.delete(request)
        db.commit()
    return request

