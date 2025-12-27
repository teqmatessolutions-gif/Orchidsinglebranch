from app.database import SessionLocal
from app.models.inventory import InventoryTransaction

db = SessionLocal()
try:
    txns = db.query(InventoryTransaction).filter(
        InventoryTransaction.transaction_type == 'out'
    ).all()
    
    print(f'Total OUT transactions: {len(txns)}')
    for t in txns[:10]:
        notes_preview = t.notes[:50] if t.notes else "N/A"
        print(f'ID: {t.id}, Item: {t.item_id}, Qty: {t.quantity}, Ref: {t.reference_number}, Notes: {notes_preview}')
finally:
    db.close()
