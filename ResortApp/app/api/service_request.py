from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestOut, ServiceRequestUpdate
from app.curd import service_request as crud
from app.utils.auth import get_db, get_current_user
from app.models.user import User
from typing import List, Optional

router = APIRouter(prefix="/service-requests", tags=["Service Requests"])

@router.post("", response_model=ServiceRequestOut)
def create_service_request(
    request: ServiceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_service_request(db, request)

@router.get("", response_model=List[ServiceRequestOut])
def get_service_requests(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_service_requests(db, skip=skip, limit=limit, status=status)

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

