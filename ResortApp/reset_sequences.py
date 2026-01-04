"""
Reset all database sequences after cleanup
This ensures auto-increment IDs start from 1 again
"""
from app.database import SessionLocal
from sqlalchemy import text

def reset_sequences():
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("RESETTING DATABASE SEQUENCES")
        print("=" * 70)
        
        # Get all sequences
        result = db.execute(text("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
        """))
        
        sequences = [row[0] for row in result]
        
        print(f"\nFound {len(sequences)} sequences to reset\n")
        
        for seq in sequences:
            try:
                db.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1"))
                print(f"✅ Reset {seq}")
            except Exception as e:
                print(f"⚠️  Could not reset {seq}: {e}")
        
        db.commit()
        
        print("\n" + "=" * 70)
        print("✅ SEQUENCES RESET COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reset_sequences()
