from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestOut, ServiceRequestUpdate
from app.curd import service_request as crud
from app.utils.auth import get_db, get_current_user
from app.models.user import User
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json

router = APIRouter(prefix="/service-requests", tags=["Service Requests"])

@router.post("", response_model=ServiceRequestOut)
def create_service_request(
    request: ServiceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_service_request(db, request)

@router.get("")
def get_service_requests(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    include_checkout_requests: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get service requests. If include_checkout_requests is True, also includes checkout requests.
    Returns a list of dicts (not ServiceRequestOut) to support both service requests and checkout requests.
    """
    service_requests = crud.get_service_requests(db, skip=skip, limit=limit, status=status)
    
    # Convert service requests to dict format
    result = []
    for sr in service_requests:
        refill_data = None
        if sr.refill_data:
            try:
                refill_data = json.loads(sr.refill_data)
            except:
                refill_data = None
        
        try:
            result.append({
                "id": sr.id,
                "food_order_id": sr.food_order_id,
                "room_id": sr.room_id,
                "employee_id": sr.employee_id,
                "request_type": str(sr.request_type) if sr.request_type else None,
                "description": str(sr.description) if sr.description else None,
                "status": str(sr.status) if sr.status else "pending",
                "created_at": sr.created_at.isoformat() if sr.created_at else None,
                "completed_at": sr.completed_at.isoformat() if sr.completed_at else None,
                "is_checkout_request": False,
                "room_number": str(getattr(sr, 'room_number', '')) if getattr(sr, 'room_number', None) else None,
                "employee_name": str(getattr(sr, 'employee_name', '')) if getattr(sr, 'employee_name', None) else None,
                "refill_data": refill_data
            })
        except Exception as e:
            print(f"[ERROR] Error converting service request {sr.id}: {e}")
            continue
    
    # Also include checkout requests as service requests
    if include_checkout_requests:
        from app.models.checkout import CheckoutRequest as CheckoutRequestModel
        from app.models.room import Room
        from app.models.inventory import InventoryItem
        from sqlalchemy.orm import joinedload
        
        checkout_query = db.query(CheckoutRequestModel).options(
            joinedload(CheckoutRequestModel.employee)
        )
        
        # Show all checkout requests except cancelled and completed ones
        if status:
            checkout_query = checkout_query.filter(CheckoutRequestModel.status == status)
        else:
            checkout_query = checkout_query.filter(
                CheckoutRequestModel.status.notin_(["cancelled", "completed"])
            )
        
        checkout_requests = checkout_query.order_by(CheckoutRequestModel.created_at.desc()).limit(limit).offset(skip).all()
        
        # Optimization: Pre-fetch all rooms to avoid N+1 queries
        room_numbers = [cr.room_number for cr in checkout_requests if cr.room_number]
        rooms = db.query(Room).filter(Room.number.in_(room_numbers)).all()
        room_map = {r.number: r for r in rooms}
        
        # Optimization: Pre-fetch all inventory items needed for hydration
        item_ids = set()
        for cr in checkout_requests:
            if cr.inventory_data:
                for item in cr.inventory_data:
                    if item.get('item_id'):
                        item_ids.add(item.get('item_id'))
        
        inventory_items = {}
        if item_ids:
            items = db.query(InventoryItem).filter(InventoryItem.id.in_(list(item_ids))).all()
            inventory_items = {i.id: i for i in items}
        
        # Convert checkout requests to service request-like format
        for cr in checkout_requests:
            room = room_map.get(str(cr.room_number))
            if room:
                try:
                    # Hydrate missing item names in inventory_data using pre-fetched map
                    enriched_inventory_data = []
                    if cr.inventory_data:
                        for item in cr.inventory_data:
                            enriched_item = item.copy()
                            # Hydrate name if missing
                            if ('item_name' not in enriched_item or not enriched_item['item_name']) and enriched_item.get('item_id'):
                                inv_item = inventory_items.get(enriched_item.get('item_id'))
                                if inv_item:
                                    enriched_item['item_name'] = inv_item.name
                                    if 'item_code' not in enriched_item:
                                        enriched_item['item_code'] = inv_item.item_code
                            enriched_inventory_data.append(enriched_item)

                    result.append({
                        "id": cr.id + 1000000, 
                        "food_order_id": None,
                        "room_id": room.id,
                        "employee_id": cr.employee_id,
                        "request_type": "checkout_verification",
                        "description": f"Checkout inventory verification for Room {cr.room_number} - Guest: {cr.guest_name}",
                        "status": str(cr.status) if cr.status else "pending",
                        "created_at": cr.created_at.isoformat() if cr.created_at else None,
                        "completed_at": cr.completed_at.isoformat() if cr.completed_at else None,
                        "is_checkout_request": True,
                        "checkout_request_id": cr.id,
                        "room_number": str(cr.room_number) if cr.room_number else None,
                        "guest_name": str(cr.guest_name) if cr.guest_name else None,
                        "employee_name": str(cr.employee.name) if cr.employee and cr.employee.name else None,
                        "inventory_notes": cr.inventory_notes,
                        # Process enriched inventory data
                        "asset_damages": [item for item in enriched_inventory_data if item.get('is_fixed_asset')],
                        "inventory_data_with_charges": [item for item in enriched_inventory_data if not item.get('is_fixed_asset')]
                    })
                except Exception as e:
                    print(f"[ERROR] Error converting checkout request {cr.id}: {e}")
                    continue
    
    return result

@router.get("/{request_id}", response_model=ServiceRequestOut)
def get_service_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    request = crud.get_service_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Service request not found")
    return request

@router.put("/{request_id}", response_model=ServiceRequestOut)
def update_service_request(
    request_id: int,
    update: ServiceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if this is a checkout request (ID > 1000000)
    if request_id > 1000000:
        # This is a checkout request, not a regular service request
        actual_checkout_id = request_id - 1000000
        
        from app.models.checkout import CheckoutRequest as CheckoutRequestModel
        checkout_request = db.query(CheckoutRequestModel).filter(
            CheckoutRequestModel.id == actual_checkout_id
        ).first()
        
        if not checkout_request:
            raise HTTPException(status_code=404, detail="Checkout request not found")
        
        # Update employee assignment
        if update.employee_id is not None:
            checkout_request.employee_id = update.employee_id
        
        # Update status if provided
        if update.status is not None:
            checkout_request.status = update.status
            if update.status == "completed":
                from datetime import datetime
                checkout_request.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(checkout_request)
        
        # Return in ServiceRequestOut format for compatibility
        from app.models.room import Room
        room = db.query(Room).filter(Room.number == checkout_request.room_number).first()
        
        return {
            "id": request_id,  # Keep the offset ID
            "food_order_id": None,
            "room_id": room.id if room else None,
            "employee_id": checkout_request.employee_id,
            "request_type": "checkout_verification",
            "description": f"Checkout inventory verification for Room {checkout_request.room_number}",
            "status": checkout_request.status,
            "created_at": checkout_request.created_at,
            "completed_at": checkout_request.completed_at
        }
    
    # Regular service request
    updated = crud.update_service_request(db, request_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Service request not found")
    return updated

@router.delete("/{request_id}")
def delete_service_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = crud.delete_service_request(db, request_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Service request not found")
    return {"message": "Service request deleted successfully"}

