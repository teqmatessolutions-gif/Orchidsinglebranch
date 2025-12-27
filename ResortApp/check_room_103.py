"""
Check if Room 103 exists in the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.room import Room

def check_room():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("CHECKING ROOM 103")
        print("=" * 60)
        
        # Check if room 103 exists
        room = db.query(Room).filter(Room.number == "103").first()
        
        if room:
            print(f"\n✓ Room 103 EXISTS in database!")
            print(f"   ID: {room.id}")
            print(f"   Number: {room.number}")
            print(f"   Type: {room.type}")
            print(f"   Price: {room.price}")
            print(f"   Status: {room.status}")
            print(f"   Image URL: {room.image_url}")
        else:
            print("\n✗ Room 103 NOT FOUND in database!")
        
        # Get all rooms
        all_rooms = db.query(Room).all()
        print(f"\n📊 Total rooms in database: {len(all_rooms)}")
        
        if len(all_rooms) > 0:
            print("\n📋 All rooms:")
            for r in all_rooms[-5:]:  # Show last 5 rooms
                print(f"   Room {r.number}: {r.type} - {r.status}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_room()
