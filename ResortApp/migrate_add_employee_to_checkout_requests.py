"""
Migration script to add employee_id and completed_at to checkout_requests table
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

def run_migration():
    print("============================================================")
    print("Add employee_id and completed_at to checkout_requests table")
    print("============================================================")

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if columns exist
        from sqlalchemy.engine import reflection
        inspector = reflection.Inspector.from_engine(engine)
        columns = [col['name'] for col in inspector.get_columns('checkout_requests')]

        from sqlalchemy import text
        
        if 'employee_id' not in columns:
            print("\nStep 1/2: Adding 'employee_id' column...")
            db.execute(text("""
                ALTER TABLE checkout_requests 
                ADD COLUMN employee_id INTEGER REFERENCES employees(id)
            """))
            db.commit()
            print("------------------------------------------------------------")
            print("✓ Added 'employee_id' column to checkout_requests table")
        else:
            print("Column 'employee_id' already exists. Skipping.")

        if 'completed_at' not in columns:
            print("\nStep 2/2: Adding 'completed_at' column...")
            db.execute(text("""
                ALTER TABLE checkout_requests 
                ADD COLUMN completed_at TIMESTAMP
            """))
            db.commit()
            print("------------------------------------------------------------")
            print("✓ Added 'completed_at' column to checkout_requests table")
        else:
            print("Column 'completed_at' already exists. Skipping.")

        print("\n============================================================")
        print("✅ Database migration completed successfully!")
        print("============================================================")

    except Exception as e:
        db.rollback()
        print(f"❌ An error occurred during migration: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()

