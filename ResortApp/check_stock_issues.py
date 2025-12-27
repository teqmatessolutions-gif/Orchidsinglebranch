"""
Check stock_issues table schema
"""
from app.database import SessionLocal
from sqlalchemy import text

def check_stock_issues():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("CHECKING STOCK_ISSUES TABLE SCHEMA")
        print("=" * 70)
        
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'stock_issues'
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        
        print("\nColumns in stock_issues table:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (nullable: {col[2]})")
        
        # Check foreign keys
        print("\n" + "=" * 70)
        print("FOREIGN KEY CONSTRAINTS")
        print("=" * 70)
        
        result = db.execute(text("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_name = 'stock_issues'
                AND tc.constraint_type = 'FOREIGN KEY';
        """))
        
        fks = result.fetchall()
        for fk in fks:
            print(f"  {fk[1]} -> {fk[2]}.{fk[3]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_stock_issues()
