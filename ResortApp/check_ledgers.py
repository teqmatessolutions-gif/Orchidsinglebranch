
import sys
import os
from sqlalchemy import func

# Add root directory to path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models.account import AccountLedger, AccountGroup

def check_equity_ledgers():
    db = SessionLocal()
    try:
        print("--- Checking Equity Ledgers ---")
        equity_group = db.query(AccountGroup).filter(AccountGroup.name == "Equity").first()
        if equity_group:
            print(f"Equity Group ID: {equity_group.id}")
            ledgers = db.query(AccountLedger).filter(AccountLedger.group_id == equity_group.id).all()
            for l in ledgers:
                print(f"- {l.name} (ID: {l.id})")
        else:
            print("Equity Group not found. Listing all groups:")
            groups = db.query(AccountGroup).all()
            for g in groups:
                 print(f"Group: {g.name} ({g.type})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_equity_ledgers()
