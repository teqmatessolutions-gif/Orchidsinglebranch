"""
Quick script to check what service-related tables exist
"""
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Get all table names
    result = db.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%service%'
        ORDER BY table_name;
    """))
    
    print("Service-related tables:")
    for row in result:
        print(f"  - {row[0]}")
        
finally:
    db.close()
