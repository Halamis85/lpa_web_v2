from app.database import SessionLocal
from app.models import ChecklistCategory

db = SessionLocal()

categories = ["5S", "Proces", "BOZP & EHS", "Kvalita"]

for c in categories:
    if not db.query(ChecklistCategory).filter_by(name=c).first():
        db.add(ChecklistCategory(name=c))

db.commit()
db.close()

print("Kategorie checklistu byly vytvořeny.")
