"""
Verify Database is Empty
"""

from sqlalchemy import text
from app.database import SessionLocal

def verify_empty():
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 60)
        print("DATABASE VERIFICATION")
        print("=" * 60)
        
        # Check key tables
        tables_to_check = [
            'bookings',
            'food_orders',
            'inventory_items',
            'rooms',
            'packages',
            'services',
            'users',
            'roles'
        ]
        
        print("\nTable Counts:")
        print("-" * 60)
        
        for table in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                status = "✓ EMPTY" if count == 0 else f"⚠ HAS {count} RECORDS"
                if table in ['users', 'roles']:
                    status = f"✓ {count} (expected)"
                print(f"{table:20} : {status}")
            except Exception as e:
                print(f"{table:20} : ERROR - {str(e)[:30]}")
        
        print("\n" + "=" * 60)
        
        # Check users
        result = db.execute(text("SELECT email FROM users"))
        users = result.fetchall()
        
        print("\nUsers in database:")
        for user in users:
            print(f"  • {user[0]}")
        
        print("\n" + "=" * 60)
        print("✅ Verification complete")
        print("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    verify_empty()
