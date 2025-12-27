"""
Test if room edits are being saved to database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.room import Room

def check_room_103():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("CHECKING ROOM 103 DETAILS")
        print("=" * 60)
        
        # Get room 103
        room = db.query(Room).filter(Room.number == "103").first()
        
        if room:
            print(f"\n✓ Room 103 found!")
            print(f"   ID: {room.id}")
            print(f"   Number: {room.number}")
            print(f"   Type: {room.type}")
            print(f"   Price: {room.price}")
            print(f"   Status: {room.status}")
            print(f"   Adults: {room.adults}")
            print(f"   Children: {room.children}")
            print(f"   Image URL: {room.image_url}")
            print(f"\n   Features:")
            print(f"   - Air Conditioning: {room.air_conditioning}")
            print(f"   - WiFi: {room.wifi}")
            print(f"   - Bathroom: {room.bathroom}")
            print(f"   - Parking: {room.parking}")
            print(f"   - Breakfast: {room.breakfast}")
        else:
            print("\n✗ Room 103 not found!")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_room_103()
