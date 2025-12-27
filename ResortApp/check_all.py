import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import text
from app.database import SessionLocal
from app.schemas.checkout import CheckoutFull
from app.models.checkout import Checkout

def check_all_validation():
    db = SessionLocal()
    try:
        # Fetch ALL objects
        orm_objs = db.query(Checkout).order_by(Checkout.id.desc()).all()
        print(f"Total objects: {len(orm_objs)}")
        
        for i, orm_obj in enumerate(orm_objs):
            try:
                # Try to validate with Pydantic
                CheckoutFull.from_orm(orm_obj)
            except Exception as e:
                print(f"Validation Failed for ID {orm_obj.id}:")
                print(e)
                return # Stop at first failure
        
        print("All records validated successfully!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_all_validation()
