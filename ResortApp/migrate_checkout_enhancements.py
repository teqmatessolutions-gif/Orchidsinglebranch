#!/usr/bin/env python3
"""
Database Migration Script for Checkout Enhancements
Run this script to add new columns for the enhanced checkout system.

Usage:
    cd ResortApp
    python migrate_checkout_enhancements.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import SQLALCHEMY_DATABASE_URL

def migrate_database():
    """Add missing columns for checkout enhancements."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("=" * 60)
        print("Checkout Enhancements - Database Migration")
        print("=" * 60)
        print()

        # Step 1: Add advance_deposit to bookings
        print("Step 1/6: Migrating 'bookings' table...")
        print("-" * 60)
        try:
            db.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS advance_deposit FLOAT DEFAULT 0.0"))
            db.commit()
            print("✓ Added 'advance_deposit' column to bookings table")
        except Exception as e:
            print(f"⚠️  advance_deposit column: {e}")
            db.rollback()
        print()

        # Step 2: Add advance_deposit to package_bookings
        print("Step 2/6: Migrating 'package_bookings' table...")
        print("-" * 60)
        try:
            db.execute(text("ALTER TABLE package_bookings ADD COLUMN IF NOT EXISTS advance_deposit FLOAT DEFAULT 0.0"))
            db.commit()
            print("✓ Added 'advance_deposit' column to package_bookings table")
        except Exception as e:
            print(f"⚠️  advance_deposit column: {e}")
            db.rollback()
        print()

        # Step 3: Create checkout_verifications table
        print("Step 3/6: Creating 'checkout_verifications' table...")
        print("-" * 60)
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS checkout_verifications (
                    id SERIAL PRIMARY KEY,
                    checkout_id INTEGER NOT NULL REFERENCES checkouts(id) ON DELETE CASCADE,
                    room_number VARCHAR NOT NULL,
                    housekeeping_status VARCHAR DEFAULT 'pending',
                    housekeeping_notes TEXT,
                    housekeeping_approved_by VARCHAR,
                    housekeeping_approved_at TIMESTAMP,
                    consumables_audit_data JSONB,
                    consumables_total_charge FLOAT DEFAULT 0.0,
                    asset_damages JSONB,
                    asset_damage_total FLOAT DEFAULT 0.0,
                    key_card_returned BOOLEAN DEFAULT FALSE,
                    key_card_fee FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_checkout_verifications_checkout_id ON checkout_verifications(checkout_id)"))
            db.commit()
            print("✓ Created 'checkout_verifications' table")
        except Exception as e:
            print(f"⚠️  checkout_verifications table: {e}")
            db.rollback()
        print()

        # Step 4: Create checkout_payments table
        print("Step 4/6: Creating 'checkout_payments' table...")
        print("-" * 60)
        try:
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS checkout_payments (
                    id SERIAL PRIMARY KEY,
                    checkout_id INTEGER NOT NULL REFERENCES checkouts(id) ON DELETE CASCADE,
                    payment_method VARCHAR NOT NULL,
                    amount FLOAT NOT NULL,
                    transaction_id VARCHAR,
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.execute(text("CREATE INDEX IF NOT EXISTS idx_checkout_payments_checkout_id ON checkout_payments(checkout_id)"))
            db.commit()
            print("✓ Created 'checkout_payments' table")
        except Exception as e:
            print(f"⚠️  checkout_payments table: {e}")
            db.rollback()
        print()

        # Step 5: Add enhanced fields to checkouts table
        print("Step 5/6: Migrating 'checkouts' table...")
        print("-" * 60)
        checkout_fields = [
            ("late_checkout_fee", "FLOAT DEFAULT 0.0"),
            ("consumables_charges", "FLOAT DEFAULT 0.0"),
            ("asset_damage_charges", "FLOAT DEFAULT 0.0"),
            ("key_card_fee", "FLOAT DEFAULT 0.0"),
            ("advance_deposit", "FLOAT DEFAULT 0.0"),
            ("tips_gratuity", "FLOAT DEFAULT 0.0"),
            ("guest_gstin", "VARCHAR"),
            ("is_b2b", "BOOLEAN DEFAULT FALSE"),
            ("invoice_number", "VARCHAR"),
            ("invoice_pdf_path", "VARCHAR"),
            ("gate_pass_path", "VARCHAR"),
            ("feedback_sent", "BOOLEAN DEFAULT FALSE"),
        ]
        
        for field_name, field_type in checkout_fields:
            try:
                db.execute(text(f"ALTER TABLE checkouts ADD COLUMN IF NOT EXISTS {field_name} {field_type}"))
                print(f"✓ Added '{field_name}' column to checkouts table")
            except Exception as e:
                print(f"⚠️  {field_name} column: {e}")
        
        # Add unique index for invoice_number if it doesn't exist
        try:
            db.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_checkouts_invoice_number ON checkouts(invoice_number) WHERE invoice_number IS NOT NULL"))
            print("✓ Created unique index on invoice_number")
        except Exception as e:
            print(f"⚠️  invoice_number index: {e}")
        
        db.commit()
        print()

        # Step 6: Verify migration
        print("Step 6/6: Verifying migration...")
        print("-" * 60)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        
        bookings_cols = [col['name'] for col in inspector.get_columns('bookings')]
        package_bookings_cols = [col['name'] for col in inspector.get_columns('package_bookings')]
        checkouts_cols = [col['name'] for col in inspector.get_columns('checkouts')]
        
        tables = inspector.get_table_names()
        
        print(f"✓ Bookings columns: {len(bookings_cols)} (advance_deposit: {'advance_deposit' in bookings_cols})")
        print(f"✓ Package bookings columns: {len(package_bookings_cols)} (advance_deposit: {'advance_deposit' in package_bookings_cols})")
        print(f"✓ Checkouts columns: {len(checkouts_cols)}")
        print(f"✓ New tables created: {'checkout_verifications' in tables}, {'checkout_payments' in tables}")
        print()

        print("=" * 60)
        print("✅ Database migration completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Restart the backend service if running")
        print("2. Verify the application is working")
        print("3. Test the checkout functionality")

    except Exception as e:
        db.rollback()
        print()
        print("=" * 60)
        print("❌ Error during database migration:")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("Please check the error above and try again.")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    migrate_database()


