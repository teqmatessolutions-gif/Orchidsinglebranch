from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.database import Base

class LostFound(Base):
    __tablename__ = "lost_found"
    
    id = Column(Integer, primary_key=True, index=True)
    item_description = Column(Text, nullable=False)  # Description of the lost/found item
    found_date = Column(Date, nullable=False, default=date.today)  # Date when item was found
    found_by = Column(String, nullable=True)  # Name of staff member who found it
    found_by_employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)  # Link to employee
    room_number = Column(String, nullable=True)  # Room number where item was found
    location = Column(String, nullable=True)  # Other location (lobby, restaurant, etc.)
    status = Column(String, default="found", nullable=False)  # found, claimed, disposed
    claimed_by = Column(String, nullable=True)  # Name of person who claimed it
    claimed_date = Column(Date, nullable=True)  # Date when item was claimed
    claimed_contact = Column(String, nullable=True)  # Contact info of claimant
    notes = Column(Text, nullable=True)  # Additional notes
    image_url = Column(String, nullable=True)  # Photo of the item
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", foreign_keys=[found_by_employee_id])
    
    def __repr__(self):
        return f"<LostFound id={self.id} item={self.item_description[:50]} status={self.status}>"

