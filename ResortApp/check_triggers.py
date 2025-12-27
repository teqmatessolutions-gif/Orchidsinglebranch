"""
Check for triggers and constraints
"""
from app.database import SessionLocal
from sqlalchemy import text

def check_triggers():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("CHECKING FOR TRIGGERS")
        print("=" * 70)
        
        # Check triggers on locations table
        result = db.execute(text("""
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers
            WHERE event_object_table = 'locations';
        """))
        
        triggers = result.fetchall()
        if triggers:
            print("\nTriggers on locations table:")
            for trig in triggers:
                print(f"  {trig[0]}: {trig[1]} - {trig[2]}")
        else:
            print("\n✅ No triggers on locations table")
        
        # Check triggers on stock_issues table
        result = db.execute(text("""
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers
            WHERE event_object_table = 'stock_issues';
        """))
        
        triggers = result.fetchall()
        if triggers:
            print("\nTriggers on stock_issues table:")
            for trig in triggers:
                print(f"  {trig[0]}: {trig[1]} - {trig[2]}")
        else:
            print("\n✅ No triggers on stock_issues table")
        
        # Check all constraints on locations
        print("\n" + "=" * 70)
        print("ALL CONSTRAINTS ON LOCATIONS TABLE")
        print("=" * 70)
        
        result = db.execute(text("""
            SELECT constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_name = 'locations';
        """))
        
        constraints = result.fetchall()
        for cons in constraints:
            print(f"  {cons[0]}: {cons[1]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_triggers()
