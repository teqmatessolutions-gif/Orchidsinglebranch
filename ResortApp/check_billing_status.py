"""
Check billing_status of assigned services
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from sqlalchemy import text

def check_billing_status():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("CHECKING ASSIGNED SERVICES BILLING STATUS")
        print("=" * 60)
        
        # Get all assigned services with billing status
        query = text("""
            SELECT 
                asv.id,
                s.name as service_name,
                r.number as room_number,
                asv.status,
                asv.billing_status,
                asv.assigned_at
            FROM assigned_services asv
            LEFT JOIN services s ON asv.service_id = s.id
            LEFT JOIN rooms r ON asv.room_id = r.id
            WHERE r.number = '102'
            ORDER BY asv.assigned_at DESC
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        print(f"\n✓ Total assigned services for Room 102: {len(rows)}")
        
        unbilled_count = 0
        billed_count = 0
        other_count = 0
        
        print("\n📋 Assigned Services for Room 102:")
        print("-" * 80)
        for row in rows:
            billing_status = row[4] or "NULL"
            if billing_status == "unbilled":
                unbilled_count += 1
                status_marker = "✓ UNBILLED"
            elif billing_status == "billed":
                billed_count += 1
                status_marker = "✗ BILLED"
            else:
                other_count += 1
                status_marker = f"? {billing_status}"
                
            print(f"   ID: {row[0]} | Service: {row[1]}")
            print(f"   Room: {row[2]} | Status: {row[3]} | Billing: {status_marker}")
            print(f"   Assigned: {row[5]}")
            print("-" * 80)
        
        print(f"\n📊 Summary:")
        print(f"   Unbilled: {unbilled_count}")
        print(f"   Billed: {billed_count}")
        print(f"   Other/NULL: {other_count}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_billing_status()
