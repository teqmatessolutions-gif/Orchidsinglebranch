from sqlalchemy.orm import Session, joinedload
from app.models.service_request import ServiceRequest
from app.models.foodorder import FoodOrder
from app.models.room import Room
from app.models.employee import Employee
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestUpdate
from typing import List, Optional
from datetime import datetime

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
        if req.employee:
            req.employee_name = req.employee.name
    
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
        if request.employee:
            request.employee_name = request.employee.name
    
    return request

def update_service_request(db: Session, request_id: int, update_data: ServiceRequestUpdate):
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if not request:
        return None
    
    if update_data.status is not None:
        request.status = update_data.status
        if update_data.status == "completed":
            request.completed_at = datetime.utcnow()
    if update_data.employee_id is not None:
        request.employee_id = update_data.employee_id
    if update_data.description is not None:
        request.description = update_data.description
    
    db.commit()
    db.refresh(request)
    return request

def delete_service_request(db: Session, request_id: int):
    request = db.query(ServiceRequest).filter(ServiceRequest.id == request_id).first()
    if request:
        db.delete(request)
        db.commit()
    return request

