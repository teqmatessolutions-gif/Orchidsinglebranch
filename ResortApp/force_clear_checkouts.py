"""
Force delete all checkouts
"""

from app.database import SessionLocal
from sqlalchemy import text

def force_clear_checkouts():
    """Force clear all checkouts"""
    
    db = SessionLocal()
    try:
        print("🧹 Force clearing all checkouts...")
        
        # Disable foreign key checks
        db.execute(text("SET session_replication_role = 'replica';"))
        
        result = db.execute(text("DELETE FROM checkouts"))
        rows = result.rowcount
        
        # Re-enable foreign key checks
        db.execute(text("SET session_replication_role = 'origin';"))
        
        db.commit()
        
        if rows > 0:
            print(f"✅ Deleted {rows} checkout(s)")
        else:
            print("✅ Checkouts table is already empty")
            
        # Verify
        result = db.execute(text("SELECT COUNT(*) FROM checkouts"))
        count = result.scalar()
        print(f"   Verification: {count} checkouts remaining")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        # Try to re-enable foreign keys
        try:
            db.execute(text("SET session_replication_role = 'origin';"))
            db.commit()
        except:
            pass
        raise
    finally:
        db.close()

if __name__ == "__main__":
    force_clear_checkouts()
