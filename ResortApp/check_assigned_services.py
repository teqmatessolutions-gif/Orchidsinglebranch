"""
Check assigned services in the database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from sqlalchemy import text

def check_assigned_services():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("CHECKING ASSIGNED SERVICES")
        print("=" * 60)
        
        # Get all assigned services with details
        query = text("""
            SELECT 
                asv.id,
                asv.service_id,
                s.name as service_name,
                asv.employee_id,
                asv.room_id,
                r.number as room_number,
                asv.status,
                asv.assigned_at
            FROM assigned_services asv
            LEFT JOIN services s ON asv.service_id = s.id
            LEFT JOIN rooms r ON asv.room_id = r.id
            ORDER BY asv.assigned_at DESC
            LIMIT 20
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        print(f"\n✓ Total assigned services: {len(rows)}")
        
        if len(rows) == 0:
            print("\n⚠️  No assigned services found!")
            print("   You need to assign services to rooms first.")
        else:
            print("\n📋 Recent Assigned Services:")
            print("-" * 60)
            for row in rows:
                print(f"   ID: {row[0]}")
                print(f"   Service: {row[2]} (ID: {row[1]})")
                print(f"   Employee ID: {row[3]}")
                print(f"   Room: {row[5]} (ID: {row[4]})")
                print(f"   Status: {row[6]}")
                print(f"   Assigned At: {row[7]}")
                print("-" * 60)
        
        # Check which rooms have checked-in bookings
        print("\n📍 Checking Checked-In Bookings:")
        booking_query = text("""
            SELECT 
                b.id,
                b.guest_name,
                b.status,
                br.room_id,
                r.number as room_number
            FROM bookings b
            LEFT JOIN booking_rooms br ON b.id = br.booking_id
            LEFT JOIN rooms r ON br.room_id = r.id
            WHERE b.status = 'checked-in'
            ORDER BY b.check_in DESC
            LIMIT 5
        """)
        
        booking_result = db.execute(booking_query)
        booking_rows = booking_result.fetchall()
        
        if len(booking_rows) == 0:
            print("   ⚠️  No checked-in bookings found!")
        else:
            print(f"   ✓ Found {len(booking_rows)} checked-in booking rooms:")
            for brow in booking_rows:
                print(f"      Booking {brow[0]}: {brow[1]} - Room {brow[4]} (ID: {brow[3]})")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_assigned_services()
