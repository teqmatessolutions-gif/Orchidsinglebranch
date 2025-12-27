"""
Check what's in the checkouts table
"""

from app.database import SessionLocal
from sqlalchemy import text

def check_checkouts():
    """Check checkouts table"""
    
    db = SessionLocal()
    try:
        print("🔍 Checking checkouts table...")
        
        result = db.execute(text("SELECT COUNT(*) FROM checkouts"))
        count = result.scalar()
        
        print(f"   Checkouts count: {count}")
        
        if count > 0:
            result = db.execute(text("SELECT id, guest_name, room_total, grand_total, checkout_date FROM checkouts LIMIT 10"))
            rows = result.fetchall()
            print("\n   Recent checkouts:")
            for row in rows:
                print(f"   - ID: {row[0]}, Guest: {row[1]}, Room Total: {row[2]}, Grand Total: {row[3]}, Date: {row[4]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_checkouts()
