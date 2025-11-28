from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ServiceRequestCreate(BaseModel):
    food_order_id: int
    room_id: int
    employee_id: Optional[int] = None
    request_type: str = "delivery"
    description: Optional[str] = None

class ServiceRequestUpdate(BaseModel):
    status: Optional[str] = None
    employee_id: Optional[int] = None
    description: Optional[str] = None

class ServiceRequestOut(BaseModel):
    id: int
    food_order_id: int
    room_id: int
    employee_id: Optional[int] = None
    request_type: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    food_order_amount: Optional[float] = None
    food_order_status: Optional[str] = None
    room_number: Optional[str] = None
    employee_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

