from sqlalchemy.orm import Session, joinedload
from app.models.lost_found import LostFound
from app.schemas.lost_found import LostFoundCreate, LostFoundUpdate
from typing import List, Optional

def create_lost_found(db: Session, lost_found_data: LostFoundCreate):
    """Create a new lost & found entry"""
    lost_found = LostFound(**lost_found_data.model_dump())
    db.add(lost_found)
    db.commit()
    db.refresh(lost_found)
    return lost_found

def get_lost_found(db: Session, lost_found_id: int):
    """Get a lost & found entry by ID"""
    return db.query(LostFound).options(
        joinedload(LostFound.employee)
    ).filter(LostFound.id == lost_found_id).first()

def get_all_lost_found(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None
):
    """Get all lost & found entries with optional status filter"""
    query = db.query(LostFound).options(
        joinedload(LostFound.employee)
    )
    
    if status:
        query = query.filter(LostFound.status == status)
    
    return query.order_by(LostFound.found_date.desc(), LostFound.created_at.desc()).offset(skip).limit(limit).all()

def update_lost_found(db: Session, lost_found_id: int, update_data: LostFoundUpdate):
    """Update a lost & found entry"""
    lost_found = db.query(LostFound).filter(LostFound.id == lost_found_id).first()
    if not lost_found:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(lost_found, key, value)
    
    db.commit()
    db.refresh(lost_found)
    return lost_found

def delete_lost_found(db: Session, lost_found_id: int):
    """Delete a lost & found entry"""
    lost_found = db.query(LostFound).filter(LostFound.id == lost_found_id).first()
    if not lost_found:
        return False
    
    db.delete(lost_found)
    db.commit()
    return True

