from app.database import SessionLocal
from app.models.account import JournalEntry, JournalEntryLine

db = SessionLocal()
try:
    # Check for consumption journal entries
    entries = db.query(JournalEntry).filter(
        JournalEntry.reference_type == 'consumption'
    ).all()
    
    print(f'Total Consumption Journal Entries: {len(entries)}')
    for entry in entries:
        print(f'\nJE Number: {entry.entry_number}')
        print(f'Reference ID: {entry.reference_id}')
        print(f'Date: {entry.entry_date}')
        print(f'Description: {entry.description}')
        print(f'Lines:')
        for line in entry.lines:
            if line.debit_ledger_id:
                print(f'  DEBIT: Ledger {line.debit_ledger_id} - ₹{line.amount}')
            if line.credit_ledger_id:
                print(f'  CREDIT: Ledger {line.credit_ledger_id} - ₹{line.amount}')
finally:
    db.close()
