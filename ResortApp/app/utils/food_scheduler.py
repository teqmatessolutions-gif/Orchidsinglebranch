import asyncio
import json
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.database import SessionLocal
from app.models.Package import PackageBooking
from app.models.service_request import ServiceRequest
from app.models.room import Room

async def run_food_scheduler():
    """Background task to check food schedules every minute"""
    print("[SCHEDULER] Starting food schedule monitor...")
    while True:
        try:
            check_food_schedules()
        except Exception as e:
            print(f"[SCHEDULER] Error: {e}")
        
        # Wait for next minute check
        # Align to next minute start for precision? No, simple sleep is fine for now
        await asyncio.sleep(60) 

def check_food_schedules():
    db = SessionLocal()
    try:
        now = datetime.now()
        current_time_str = now.strftime("%H:%M") # e.g. "08:00"
        
        # Get active checked-in bookings
        # Join package to access food_timing
        active_bookings = (
            db.query(PackageBooking)
            .options(joinedload(PackageBooking.package))
            .options(joinedload(PackageBooking.rooms))
            .filter(PackageBooking.status.in_(['checked-in', 'checked_in']))
            .all()
        )
        
        count = 0
        for booking in active_bookings:
            if not booking.package or not booking.package.food_timing:
                continue
                
            try:
                # Parse JSON timing schedule: {"Breakfast": "08:00", "Lunch": "13:00"}
                if isinstance(booking.package.food_timing, str):
                    timings = json.loads(booking.package.food_timing)
                else:
                    timings = booking.package.food_timing # Already dict or none
                
                if not timings or not isinstance(timings, dict):
                    continue
                    
            except Exception as e:
                # print(f"Error parsing timing for booking {booking.id}: {e}")
                continue
                
            for meal, time_str in timings.items():
                # Check if current time matches scheduled time
                if time_str == current_time_str:
                    
                    # For each room in this booking, create a service request
                    for room_link in booking.rooms:
                        room_id = room_link.room_id
                        
                        # Check duplicate: Prevent creating multiple requests for same meal same day
                        # Filter by room_id and description matching today
                        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
                        
                        exists = db.query(ServiceRequest).filter(
                             ServiceRequest.room_id == room_id,
                             ServiceRequest.description.like(f"Auto-Scheduled {meal}%"),
                             ServiceRequest.created_at >= start_of_day
                        ).first()
                        
                        if not exists:
                            # Create Request
                            print(f"[AUTO-SCHEDULER] Creating {meal} request for Room {room_id}")
                            req = ServiceRequest(
                                room_id=room_id,
                                request_type="food_delivery",
                                description=f"Auto-Scheduled {meal} (Package: {booking.package.title})",
                                status="pending",
                                created_at=now
                            )
                            db.add(req)
                            count += 1
                            
        if count > 0:
            db.commit()
            print(f"[AUTO-SCHEDULER] Created {count} service requests for {current_time_str}")
            
    except Exception as e:
        print(f"Error in check_food_schedules: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
