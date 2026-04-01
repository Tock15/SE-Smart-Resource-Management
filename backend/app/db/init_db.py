from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import user, resource, booking
from app.services.authService import AuthService

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        admin_exists = db.query(user.Admin).first()
        if not admin_exists:
            print("Seeding Admin...")
            new_admin = user.Admin(
                username="admin",
                email="admin@sesrm.com",
                hashed_password=AuthService.hash_password("password"),
                role="admin"
            )
            db.add(new_admin)
        else:
            print("Admin already exists, skipping...")
        
        user_exists = db.query(user.User).filter_by(username="student1").first()
        if not user_exists:
            print("Seeding Student...")
            new_student = user.Student(
                username="student1",
                email="student1@gmail.com",
                hashed_password=AuthService.hash_password("password"),
                role="student",
                student_id="S1234567"
            )
            db.add(new_student)
        else:
            print("Student1already exists, skipping...")

        # 3. Seed Co-Working Space
        space_exists = db.query(resource.CoWorkingSpace).filter_by(room_no="402").first()
        if not space_exists:
            print("Seeding Co-Working Space...")
            new_space = resource.CoWorkingSpace(
                name="Innovation Hub",
                description="Study area with high-speed WiFi",
                type="coworking_space",
                room_no="402",
                capacity=10
            )
            db.add(new_space)
        else:
            print("Co-Working Space 402 already exists, skipping...")
        space_exists2= db.query(resource.CoWorkingSpace).filter_by(room_no="806").first()
        if not space_exists:
            print("Seeding Co-Working Space...")
            new_space = resource.CoWorkingSpace(
                name="Creative Corner",
                description="Inspiration zone with art supplies",
                type="coworking_space",
                room_no="806",
                capacity=8
            )
            db.add(new_space)
        else:
            print("Co-Working Space 806 already exists, skipping...")
        # 4. Seed Locker
        locker_exists = db.query(resource.Locker).filter_by(locker_no="L-101").first()
        if not locker_exists:
            print("Seeding Locker...")
            new_locker = resource.Locker(
                name="West Wing Locker",
                type="locker",
                locker_no="L-101"
            )
            db.add(new_locker)
        else:
            print("Locker L-101 already exists, skipping...")
        
        # 5. Seed Booking
        booking_exists = db.query(booking.Booking).first()
        if not booking_exists:
            print("Seeding Booking...")
            timeslot = booking.Timeslot(
                start_time="2024-07-01 10:00:00",
                end_time="2024-07-01 12:00:00")
            new_booking = booking.Booking(
                user_id=2,
                resource_id=1,
                timeslot=timeslot
            )
            db.add(new_booking)
        else:
            print("Booking already exists, skipping...")
        

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()