"""
Drop unique constraint on barcode column
Barcode should be optional and not require uniqueness when NULL
"""
from app.database import SessionLocal
from sqlalchemy import text

def drop_barcode_unique_constraint():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("DROPPING UNIQUE CONSTRAINT ON BARCODE")
        print("=" * 70)
        
        # Drop the unique index
        db.execute(text("DROP INDEX IF EXISTS ix_inventory_items_barcode"))
        db.commit()
        
        print("✅ Unique constraint on barcode dropped successfully")
        print("\nBarcode column is now optional and allows duplicates/NULLs")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    drop_barcode_unique_constraint()
