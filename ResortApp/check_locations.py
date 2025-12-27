from app.utils.auth import get_db
from app.models.inventory import Location
db = next(get_db())

locations = db.query(Location).filter(Location.location_type.in_(["CENTRAL_WAREHOUSE", "WAREHOUSE", "BRANCH_STORE", "STORE", "STORAGE"])).all()

print(f"{'ID':<5} | {'Name':<20} | {'Type':<15} | {'Building':<15} | {'Room Area':<15}")
print("-" * 80)
for loc in locations:
    print(f"{loc.id:<5} | {loc.name:<20} | {loc.location_type:<15} | {str(loc.building):<15} | {str(loc.room_area):<15}")
