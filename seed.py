"""
Seed file to generate demo data for the Trekking Management Application.
Run this script: python seed.py
"""
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app
from models import db, User, Trek, Booking

first_names = ["Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Sam", "Jamie", "Chris", "Pat", "Drew", "Cameron", "Jesse", "Avery", "Dakota", "Peyton", "Skyler", "Reese", "Rowan", "Hayden", "Quinn", "Parker", "Emerson", "Finley", "Blake"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris"]

trek_names = ["Everest Base Camp", "Annapurna Circuit", "Inca Trail", "Kilimanjaro", "Tour du Mont Blanc", "Patagonia W Trek", "Zion Narrows", "Grand Canyon Rim", "Yosemite Half Dome", "Kalalau Trail", "Laugavegur Trail", "Routeburn Track", "West Highland Way"]
locations = ["Nepal", "Peru", "Tanzania", "France", "Chile", "USA", "Iceland", "New Zealand", "Scotland"]
difficulties = ["Easy", "Moderate", "Hard"]
statuses = ["Pending", "Approved", "Open", "Closed", "Completed"]

def generate_phone():
    return f"+1{random.randint(1000000000, 9999999999)}"

with app.app_context():
    print("Clearing old data (keeping admin)...")
    db.session.query(Booking).delete()
    db.session.query(Trek).delete()
    db.session.query(User).filter(User.role != "admin").delete()
    db.session.commit()

    print("Generating 15 Staff members...")
    staff_list = []
    for i in range(15):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        u = User(
            username=f"staff_{fname.lower()}_{i+1}",
            email=f"staff{i+1}@trekking.com",
            password=generate_password_hash("password123"),
            full_name=f"{fname} {lname} (Staff)",
            phone=generate_phone(),
            role="staff"
        )
        db.session.add(u)
        staff_list.append(u)
    db.session.commit()

    print("Generating 10 Treks...")
    trek_list = []
    for i in range(10):
        t_name = random.choice(trek_names)
        slots = random.randint(15, 50)
        start_dt = datetime.utcnow() + timedelta(days=random.randint(-10, 60))
        end_dt = start_dt + timedelta(days=random.randint(2, 14))
        
        status = random.choice(statuses)
        if start_dt < datetime.utcnow() and status not in ["Completed", "Closed"]:
            status = "Open"
            
        t = Trek(
            name=f"{t_name} Expedition {i+1}",
            location=random.choice(locations),
            difficulty=random.choice(difficulties),
            duration_days=(end_dt - start_dt).days,
            total_slots=slots,
            available_slots=slots,
            assigned_staff_id=random.choice(staff_list).id,
            status=status,
            start_date=start_dt.strftime("%Y-%m-%d"),
            end_date=end_dt.strftime("%Y-%m-%d"),
            description=f"Experience the ultimate adventure at {t_name} with breathtaking views and unforgettable trails.",
            price=round(random.uniform(100, 2000), 2),
            altitude=f"{random.randint(2000, 6000)}m"
        )
        db.session.add(t)
        trek_list.append(t)
    db.session.commit()

    print("Generating 50 Users (Trekkers)...")
    user_list = []
    for i in range(50):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        u = User(
            username=f"trekker_{fname.lower()}_{i+1}",
            email=f"user{i+1}@trekking.com",
            password=generate_password_hash("password123"),
            full_name=f"{fname} {lname}",
            phone=generate_phone(),
            role="user"
        )
        db.session.add(u)
        user_list.append(u)
    db.session.commit()

    print("Generating random Bookings...")
    bookable_treks = [t for t in trek_list if t.status in ["Open", "Approved", "Completed", "Closed"]]
    if bookable_treks:
        for u in user_list:
            # Each user makes 0 to 4 random bookings
            for _ in range(random.randint(0, 4)):
                tk = random.choice(bookable_treks)
                
                # Check for duplicates
                if not Booking.query.filter_by(user_id=u.id, trek_id=tk.id).first():
                    if tk.available_slots > 0:
                        # Determine booking status based on trek status
                        if tk.status == "Completed":
                            b_status = "Completed"
                        elif tk.status == "Closed":
                            b_status = random.choice(["Completed", "Cancelled"])
                        else:
                            b_status = random.choice(["Booked", "Booked", "Booked", "Cancelled"])
                            
                        b = Booking(
                            user_id=u.id,
                            trek_id=tk.id,
                            status=b_status,
                            booking_date=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                        )
                        db.session.add(b)
                        
                        # Only decrement slots if it's currently holding a spot
                        if b_status in ["Booked", "Completed"]:
                            tk.available_slots -= 1
    db.session.commit()
    print("Database seeded successfully! (Passwords are 'password123')")
