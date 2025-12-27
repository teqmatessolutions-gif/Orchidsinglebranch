from app.database import SessionLocal
from app.models.service_request import ServiceRequest

db = SessionLocal()

print("=" * 80)
print("SERVICE REQUESTS - Checking for data issues")
print("=" * 80)

# Get recent service requests
requests = db.query(ServiceRequest).order_by(ServiceRequest.id.desc()).limit(10).all()

for req in requests:
    print(f"\nID: {req.id}")
    print(f"Room ID: {req.room_id}")
    print(f"Request Type: {req.request_type}")
    print(f"Description: {req.description[:100] if req.description else 'None'}...")
    print(f"Status: {req.status}")
    print(f"Employee ID: {req.employee_id}")
    print(f"Food Order ID: {req.food_order_id}")
    print("-" * 80)

db.close()
