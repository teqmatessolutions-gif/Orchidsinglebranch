from app.database import SessionLocal
from app.models.inventory import PurchaseMaster
from app.models.account import JournalEntry

db = SessionLocal()
try:
    purchases = db.query(PurchaseMaster).all()
    print(f"Total Purchases: {len(purchases)}")
    for p in purchases:
        je_count = db.query(JournalEntry).filter(
            JournalEntry.reference_type == 'purchase',
            JournalEntry.reference_id == p.id
        ).count()
        print(f"ID: {p.id}, Status: {p.status}, Number: {p.purchase_number}, JE Exists: {je_count > 0}")
finally:
    db.close()
