from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.booking import Booking
from app.models.room import Room

def check_booking_status():
    db = SessionLocal()
    try:
        # Find booking BK-000020 (ID 20)
        booking = db.query(Booking).filter(Booking.id == 20).first()
        
        if booking:
            print(f"Booking ID: BK-{str(booking.id).zfill(6)}")
            print(f"Guest Name: {booking.guest_name}")
            print(f"Status: {booking.status}")
            print(f"Check-in Date: {booking.check_in}")
            print(f"Check-out Date: {booking.check_out}")
            
            # Check rooms
            if booking.booking_rooms:
                print(f"\nRooms ({len(booking.booking_rooms)}):")
                for br in booking.booking_rooms:
                    if br.room:
                        print(f"  - Room {br.room.number}: Status = {br.room.status}")
            else:
                print("\nNo rooms assigned")
                
        else:
            print("Booking not found")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_booking_status()
