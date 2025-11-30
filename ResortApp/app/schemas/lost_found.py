from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date

class LostFoundBase(BaseModel):
    item_description: str
    found_date: date
    found_by: Optional[str] = None
    found_by_employee_id: Optional[int] = None
    room_number: Optional[str] = None
    location: Optional[str] = None
    status: str = "found"  # found, claimed, disposed
    claimed_by: Optional[str] = None
    claimed_date: Optional[date] = None
    claimed_contact: Optional[str] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None

class LostFoundCreate(LostFoundBase):
    pass

class LostFoundUpdate(BaseModel):
    item_description: Optional[str] = None
    found_date: Optional[date] = None
    found_by: Optional[str] = None
    found_by_employee_id: Optional[int] = None
    room_number: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    claimed_by: Optional[str] = None
    claimed_date: Optional[date] = None
    claimed_contact: Optional[str] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None

class LostFoundOut(LostFoundBase):
    id: int
    created_at: datetime
    updated_at: datetime
    employee_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

