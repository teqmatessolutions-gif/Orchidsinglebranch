
import sys
import os
import json
from sqlalchemy import func

# Add root directory to path
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models.account import AccountLedger, AccountGroup

def list_account_groups():
    db = SessionLocal()
    try:
        print("--- Listing Account Groups ---")
        groups = db.query(AccountGroup).all()
        for g in groups:
            print(f"ID: {g.id} | Name: {g.name} | Type: {g.account_type}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_account_groups()
