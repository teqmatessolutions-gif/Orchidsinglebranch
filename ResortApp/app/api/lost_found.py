from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas.lost_found import LostFoundCreate, LostFoundOut, LostFoundUpdate
from app.curd import lost_found as crud
from app.utils.auth import get_db, get_current_user
from app.models.user import User
from typing import List, Optional
import os
import shutil
import uuid

router = APIRouter(prefix="/lost-found", tags=["Lost & Found"])

UPLOAD_DIR = "static/uploads/lost_found"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("", response_model=LostFoundOut)
def create_lost_found(
    item_description: str = Form(...),
    found_date: str = Form(...),
    found_by: Optional[str] = Form(None),
    found_by_employee_id: Optional[int] = Form(None),
    room_number: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    status: str = Form("found"),
    notes: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new lost & found entry"""
    try:
        from datetime import datetime
        found_date_obj = datetime.strptime(found_date, "%Y-%m-%d").date()
        
        # Handle image upload
        image_url = None
        if image and image.filename:
            filename = f"lost_found_{uuid.uuid4().hex}_{image.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_url = f"static/uploads/lost_found/{filename}".replace("\\", "/")
        
        lost_found_data = LostFoundCreate(
            item_description=item_description,
            found_date=found_date_obj,
            found_by=found_by,
            found_by_employee_id=found_by_employee_id,
            room_number=room_number,
            location=location,
            status=status,
            notes=notes,
            image_url=image_url
        )
        
        created = crud.create_lost_found(db, lost_found_data)
        
        # Load employee relationship for response
        result = {
            **created.__dict__,
            "employee_name": created.employee.name if created.employee else None
        }
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating lost & found entry: {str(e)}")

@router.get("", response_model=List[LostFoundOut])
def get_lost_found_items(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all lost & found items with optional status filter"""
    items = crud.get_all_lost_found(db, skip=skip, limit=limit, status=status)
    result = []
    for item in items:
        result.append({
            **item.__dict__,
            "employee_name": item.employee.name if item.employee else None
        })
    return result

@router.get("/{item_id}", response_model=LostFoundOut)
def get_lost_found_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific lost & found item"""
    item = crud.get_lost_found(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Lost & found item not found")
    
    return {
        **item.__dict__,
        "employee_name": item.employee.name if item.employee else None
    }

@router.put("/{item_id}", response_model=LostFoundOut)
def update_lost_found_item(
    item_id: int,
    item_description: Optional[str] = Form(None),
    found_date: Optional[str] = Form(None),
    found_by: Optional[str] = Form(None),
    found_by_employee_id: Optional[int] = Form(None),
    room_number: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    claimed_by: Optional[str] = Form(None),
    claimed_date: Optional[str] = Form(None),
    claimed_contact: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a lost & found item"""
    item = crud.get_lost_found(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Lost & found item not found")
    
    try:
        update_dict = {}
        if item_description is not None:
            update_dict["item_description"] = item_description
        if found_date is not None:
            from datetime import datetime
            update_dict["found_date"] = datetime.strptime(found_date, "%Y-%m-%d").date()
        if found_by is not None:
            update_dict["found_by"] = found_by
        if found_by_employee_id is not None:
            update_dict["found_by_employee_id"] = found_by_employee_id
        if room_number is not None:
            update_dict["room_number"] = room_number
        if location is not None:
            update_dict["location"] = location
        if status is not None:
            update_dict["status"] = status
        if claimed_by is not None:
            update_dict["claimed_by"] = claimed_by
        if claimed_date is not None:
            from datetime import datetime
            update_dict["claimed_date"] = datetime.strptime(claimed_date, "%Y-%m-%d").date()
        if claimed_contact is not None:
            update_dict["claimed_contact"] = claimed_contact
        if notes is not None:
            update_dict["notes"] = notes
        
        # Handle image upload
        if image and image.filename:
            filename = f"lost_found_{uuid.uuid4().hex}_{image.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            update_dict["image_url"] = f"static/uploads/lost_found/{filename}".replace("\\", "/")
        
        update_data = LostFoundUpdate(**update_dict)
        updated = crud.update_lost_found(db, item_id, update_data)
        
        if not updated:
            raise HTTPException(status_code=404, detail="Lost & found item not found")
        
        # Reload with relationships
        updated_item = crud.get_lost_found(db, item_id)
        return {
            **updated_item.__dict__,
            "employee_name": updated_item.employee.name if updated_item.employee else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating lost & found item: {str(e)}")

@router.delete("/{item_id}")
def delete_lost_found_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a lost & found item"""
    deleted = crud.delete_lost_found(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lost & found item not found")
    return {"message": "Lost & found item deleted successfully"}

