from app import app
from models import db, Household, Guest

with app.app_context():
    db.create_all()

    # Add a sample household
    h = Household(name="Smith")
    db.session.add(h)
    db.session.commit()

    # Add a couple of guests
    guests = [
        Guest(full_name="Jane Smith", household_id=h.id),
        Guest(full_name="John Smith", household_id=h.id)
    ]
    db.session.add_all(guests)
    db.session.commit()

print("Database initialized with sample data.")
