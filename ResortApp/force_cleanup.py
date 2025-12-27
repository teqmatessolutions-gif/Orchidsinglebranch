"""
Aggressive cleanup - Force clear the stubborn tables
"""
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("🔥 FORCE CLEARING STUBBORN TABLES...\n")
    
    # Disable foreign keys
    db.execute(text("SET session_replication_role = 'replica';"))
    
    # Force delete from the 3 tables that won't clear
    tables = [
        ("checkout_requests", "Checkout Requests"),
        ("checkouts", "Completed Checkouts"),
        ("waste_logs", "Waste Logs"),
    ]
    
    for table_name, display_name in tables:
        try:
            result = db.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
            print(f"   ✓ TRUNCATED {display_name}")
            db.commit()  # Commit immediately after each table
        except Exception as e:
            print(f"   ⚠ Could not truncate {display_name}: {e}")
            db.rollback()
            # Try DELETE instead
            try:
                result = db.execute(text(f"DELETE FROM {table_name}"))
                print(f"   ✓ DELETED ALL from {display_name}: {result.rowcount} rows")
                db.commit()
            except Exception as e2:
                print(f"   ❌ Failed to clear {display_name}: {e2}")
                db.rollback()
    
    # Re-enable foreign keys
    db.execute(text("SET session_replication_role = 'origin';"))
    db.commit()
    
    print("\n✅ Force cleanup complete!")
    
    # Verify
    print("\n🔍 Verifying...")
    for table_name, display_name in tables:
        result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        status = "✅ EMPTY" if count == 0 else f"❌ Still has {count} rows"
        print(f"   {display_name:25s} {status}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    db.rollback()
finally:
    db.close()
