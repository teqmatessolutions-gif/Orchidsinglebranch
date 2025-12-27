"""
Test package update functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.Package import Package

def check_packages():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("CHECKING PACKAGES")
        print("=" * 60)
        
        # Get all packages
        packages = db.query(Package).all()
        
        print(f"\n✓ Total packages in database: {len(packages)}")
        
        if len(packages) > 0:
            print("\n📋 All packages:")
            for pkg in packages:
                print(f"\n   ID: {pkg.id}")
                print(f"   Title: {pkg.title}")
                print(f"   Description: {pkg.description}")
                print(f"   Price: {pkg.price}")
                print(f"   Booking Type: {pkg.booking_type}")
                print(f"   Room Types: {pkg.room_types}")
                print(f"   Images: {len(pkg.images) if pkg.images else 0}")
                print("-" * 60)
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_packages()
