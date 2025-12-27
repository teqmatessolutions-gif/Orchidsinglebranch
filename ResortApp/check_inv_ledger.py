
import sys
import os
from sqlalchemy import func

# Add root directory to path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models.account import AccountLedger, JournalEntryLine, JournalEntry

def check_inventory_ledger_lines():
    db = SessionLocal()
    try:
        print("--- Checking Inventory Ledger Lines ---")
        inv_ledger = db.query(AccountLedger).filter(AccountLedger.name == "Inventory Asset (Stock)").first()
        
        lines = db.query(JournalEntryLine).filter(
             (JournalEntryLine.debit_ledger_id == inv_ledger.id) | 
             (JournalEntryLine.credit_ledger_id == inv_ledger.id)
        ).all()
        
        total_debit = 0
        total_credit = 0
        
        for line in lines:
            je = db.query(JournalEntry).get(line.entry_id)
            if line.debit_ledger_id == inv_ledger.id:
                print(f"[DR] {line.amount:,.2f} | Ref: {je.reference_type} #{je.reference_id} | Desc: {je.description}")
                total_debit += line.amount
            else:
                print(f"[CR] {line.amount:,.2f} | Ref: {je.reference_type} #{je.reference_id} | Desc: {je.description}")
                total_credit += line.amount
                
        print(f"Total Debit: {total_debit:,.2f}")
        print(f"Total Credit: {total_credit:,.2f}")
        print(f"Net Balance: {total_debit - total_credit:,.2f}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_inventory_ledger_lines()
