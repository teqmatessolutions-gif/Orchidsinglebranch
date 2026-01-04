from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
users = db.query(User).all()
print("Existing Users:")
for u in users:
    print(f"ID: {u.id}, Email: {u.email}, Name: {u.name}, Role: {u.role.name if u.role else 'None'}")
