"""
Check if services exist in the database and test the API endpoint
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.service import Service
from sqlalchemy import text

def check_services():
    db = SessionLocal()
    try:
        # Check if services table exists
        print("=" * 60)
        print("CHECKING SERVICES IN DATABASE")
        print("=" * 60)
        
        # Count services
        count = db.query(Service).count()
        print(f"\n✓ Total services in database: {count}")
        
        if count == 0:
            print("\n⚠️  WARNING: No services found in the database!")
            print("   You need to create services first.")
            print("   Go to the Services page in the dashboard to create services.")
        else:
            # List all services
            services = db.query(Service).all()
            print("\n📋 Services List:")
            print("-" * 60)
            for svc in services:
                print(f"   ID: {svc.id}")
                print(f"   Name: {svc.name}")
                print(f"   Charges: ₹{svc.charges}")
                print(f"   Description: {svc.description}")
                print(f"   Visible to Guest: {getattr(svc, 'is_visible_to_guest', False)}")
                print("-" * 60)
        
        # Check assigned services
        assigned_count = db.execute(text("SELECT COUNT(*) FROM assigned_services")).scalar()
        print(f"\n✓ Total assigned services: {assigned_count}")
        
        print("\n" + "=" * 60)
        print("DATABASE CHECK COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_services()
