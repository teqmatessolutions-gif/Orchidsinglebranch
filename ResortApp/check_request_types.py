from app.database import SessionLocal
from app.models.service_request import ServiceRequest

db = SessionLocal()

print("=" * 80)
print("SERVICE REQUEST TYPES - Checking current data")
print("=" * 80)

# Get all unique request types
from sqlalchemy import distinct

request_types = db.query(distinct(ServiceRequest.request_type)).all()

print("\nUnique Request Types in Database:")
for (rt,) in request_types:
    count = db.query(ServiceRequest).filter(ServiceRequest.request_type == rt).count()
    print(f"  - {rt}: {count} requests")

print("\n" + "=" * 80)
print("Recent Service Requests:")
print("=" * 80)

requests = db.query(ServiceRequest).order_by(ServiceRequest.id.desc()).limit(5).all()

for req in requests:
    print(f"\nID: {req.id} | Room: {req.room_id} | Type: '{req.request_type}'")
    print(f"Description: {req.description[:80] if req.description else 'None'}...")
    print(f"Status: {req.status}")

db.close()
