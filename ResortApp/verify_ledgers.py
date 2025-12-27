
import sys
import os
from sqlalchemy import func

# Add root directory to path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models.account import AccountLedger, JournalEntryLine

def verify_ledger_balances():
    db = SessionLocal()
    try:
        print("--- Verifying Ledger Balances (Journal Lines) ---")
        
        # Get all ledgers with non-zero balance
        ledgers = db.query(AccountLedger).order_by(AccountLedger.name).all()
        
        for ledger in ledgers:
            # Calculate balance from lines
            # Debit (+), Credit (-) for Assets/Expenses? 
            # Usually: 
            # Asset/Expense: Debit is positive.
            # Liability/Income: Credit is positive (but stored as negative or handled by side).
            
            debits = db.query(func.sum(JournalEntryLine.amount))\
                .filter(JournalEntryLine.debit_ledger_id == ledger.id)\
                .scalar() or 0.0
                
            credits = db.query(func.sum(JournalEntryLine.amount))\
                .filter(JournalEntryLine.credit_ledger_id == ledger.id)\
                .scalar() or 0.0
            
            balance = debits - credits
            
            # Simple heuristic for display
            if abs(balance) > 0.01:
                print(f"Ledger: {ledger.name:<30} | Debits: {debits:,.2f} | Credits: {credits:,.2f} | Net: {balance:,.2f}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_ledger_balances()
