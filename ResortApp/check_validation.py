import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import text
from app.database import SessionLocal
from app.schemas.checkout import CheckoutFull
from app.models.checkout import Checkout

def check_validation():
    db = SessionLocal()
    try:
        # Fetch the ORM object directly
        orm_obj = db.query(Checkout).order_by(Checkout.id.desc()).first()
        
        if orm_obj:
            print(f"Checkout ID: {orm_obj.id}")
            try:
                # Try to validate with Pydantic
                model_obj = CheckoutFull.from_orm(orm_obj)
                print("Validation Successful!")
                print(model_obj.dict())
            except Exception as e:
                print("Validation Failed:")
                print(e)
        else:
            print("No checkouts found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_validation()
