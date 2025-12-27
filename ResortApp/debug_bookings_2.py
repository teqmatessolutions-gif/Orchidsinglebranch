
from app.models.booking import Booking
from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload, sessionmaker

DATABASE_URL = "postgresql://postgres:qwerty123@localhost:5432/orchiddb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

bookings = db.query(Booking).options(joinedload(Booking.booking_rooms)).order_by(Booking.id.desc()).limit(5).all()
for b in bookings:
    print(f"Booking {b.id}: Status {b.status} Guest {b.guest_name}")
    for br in b.booking_rooms:
        print(f"  - Room {br.room.number} (ID {br.room_id})")
