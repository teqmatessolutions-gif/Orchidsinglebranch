
import sys
import os
sys.path.append(os.getcwd())
from app.database import SessionLocal
from app.models.account import AccountLedger, AccountGroup

def check_ledger_details():
    db = SessionLocal()
    try:
        print("--- Checking Ledger Groups ---")
        
        names = ["Input CGST", "Accounts Payable (Vendor)", "Inventory Asset (Stock)"]
        
        for name in names:
            ledger = db.query(AccountLedger).filter(AccountLedger.name == name).first()
            if ledger:
                group = db.query(AccountGroup).get(ledger.group_id)
                print(f"Ledger: {ledger.name}")
                print(f"  - Balance Type: {ledger.balance_type}")
                print(f"  - Group: {group.name} (Type: {group.account_type})")
                print(f"  - ID: {ledger.id}")
            else:
                print(f"Ledger {name} not found")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_ledger_details()
