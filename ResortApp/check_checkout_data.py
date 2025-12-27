import os
import sys
from dotenv import load_dotenv
import json

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
print(f"Loaded .env from: {env_path}")

# Add the ResortApp directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.checkout import CheckoutRequest

db = SessionLocal()

print("\n=== Checking Checkout Request Data ===\n")

# Find the most recent checkout request for Room 103
checkout = db.query(CheckoutRequest).filter(
    CheckoutRequest.room_number.ilike("%103%"),
    CheckoutRequest.status == "completed"
).order_by(CheckoutRequest.id.desc()).first()

if not checkout:
    print("No completed checkout request found for Room 103")
    db.close()
    exit()

print(f"Checkout Request ID: {checkout.id}")
print(f"Room: {checkout.room_number}")
print(f"Status: {checkout.status}")
print(f"\nInventory Data:")
print(json.dumps(checkout.inventory_data, indent=2))

db.close()
