"""
Migration script to create checkout_requests table
"""
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Text, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

Base = declarative_base()

def run_migration():
    print("============================================================")
    print("Create checkout_requests table")
    print("============================================================")

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if table exists
        from sqlalchemy.engine import reflection
        inspector = reflection.Inspector.from_engine(engine)
        tables = inspector.get_table_names()

        if 'checkout_requests' not in tables:
            print("\nStep 1/1: Creating 'checkout_requests' table...")
            
            # Create the table
            db.execute("""
                CREATE TABLE checkout_requests (
                    id SERIAL PRIMARY KEY,
                    booking_id INTEGER REFERENCES bookings(id),
                    package_booking_id INTEGER REFERENCES package_bookings(id),
                    room_number VARCHAR NOT NULL,
                    guest_name VARCHAR NOT NULL,
                    status VARCHAR DEFAULT 'pending',
                    requested_by VARCHAR,
                    requested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    inventory_checked BOOLEAN DEFAULT FALSE,
                    inventory_checked_by VARCHAR,
                    inventory_checked_at TIMESTAMP,
                    inventory_notes TEXT,
                    checkout_id INTEGER REFERENCES checkouts(id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """)
            
            db.commit()
            print("------------------------------------------------------------")
            print("✓ Created 'checkout_requests' table")
        else:
            print("Table 'checkout_requests' already exists. Skipping.")

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


