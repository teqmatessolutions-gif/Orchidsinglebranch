
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.inventory import InventoryItem, Location, LocationStock, InventoryTransaction
import os

# Setup DB connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:qwerty123@localhost:5432/orchid_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # 1. Find the Item
    towel = db.query(InventoryItem).filter(InventoryItem.name.ilike("%Kitchen Hand Towel%")).first()
    
    # Check for "Laundry Queue" location
    lq = db.query(Location).filter(Location.name.ilike("%Laundry Queue%")).first()
    if lq:
        print(f"✅ Found Location 'Laundry Queue': ID {lq.id}")
    else:
        print("❌ Location 'Laundry Queue' NOT found.")

    if not towel:
        print("❌ 'Kitchen Hand Towel' not found in database.")
    else:
        print(f"✅ Found Item: '{towel.name}' (ID: {towel.id})")
        print(f"   - Track Laundry Cycle: {towel.track_laundry_cycle}")
        
        # 2. Check Stocks
        print("\n=== Current Stock Locations ===")
        stocks = db.query(LocationStock).filter(LocationStock.item_id == towel.id, LocationStock.quantity > 0).all()
        for stock in stocks:
            loc = db.query(Location).filter(Location.id == stock.location_id).first()
            loc_name = loc.name if loc else f"Loc-{stock.location_id}"
            print(f"   - {loc_name} (ID: {stock.location_id}): {stock.quantity}")

        # 3. Check Recent Transactions (Last 5)
        print("\n=== Recent Transactions ===")
        txs = db.query(InventoryTransaction).filter(InventoryTransaction.item_id == towel.id).order_by(InventoryTransaction.created_at.desc()).limit(5).all()
        for tx in txs:
            print(f"   - {tx.created_at}: {tx.transaction_type} {tx.quantity} pcs. Notes: {tx.notes}")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
