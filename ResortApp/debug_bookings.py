
from app.models.booking import Booking
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:qwerty123@localhost:5432/orchiddb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

bookings = db.query(Booking).order_by(Booking.id.desc()).limit(5).all()
for b in bookings:
    print(f"Booking {b.booking_reference}: Status {b.status}")
    for br in b.booking_rooms:
        print(f"  - Room {br.room.number} (ID {br.room_id})")
