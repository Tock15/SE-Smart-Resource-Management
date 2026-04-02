from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import user, resource, booking
from app.services.authService import AuthService
from datetime import datetime

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
        # Seed additional students
        for i in range(2, 6):
            student_exists = db.query(user.User).filter_by(username=f"student{i}").first()
            if not student_exists:
                print(f"Seeding Student{i}...")
                new_student = user.Student(
                    username=f"student{i}",
                    email=f"student{i}@gmail.com",
                    hashed_password=AuthService.hash_password("password"),
                    role="student",
                    student_id=f"S123456{i}"
                )
                db.add(new_student)
            else:
                print(f"Student{i} already exists, skipping...")
        # seed teacher account
        teacher_exists = db.query(user.User).filter_by(username="teacher1").first()
        if not teacher_exists:
            print("Seeding Teacher...")
            new_teacher = user.Teacher(
                username="teacher1",
                email="teacher1@gmail.com",
                hashed_password=AuthService.hash_password("password"),
                role="teacher"
            )
            db.add(new_teacher)
        else:
            print("Teacher1 already exists, skipping...")
        

       # 3. Seed Co-Working Spaces
        # Space 1: Innovation Hub
        space_exists = db.query(resource.CoWorkingSpace).filter_by(room_no="402").first()
        if not space_exists:
            print("Seeding Innovation Hub...")
            new_space = resource.CoWorkingSpace(
                name="Innovation Hub",
                description="Study area with high-speed WiFi",
                type="coworking_space",
                room_no="402",
                capacity=10,
                min_guests=2,       # Requires at least 2 people to book
                image_url=None      # Leaving blank as requested
            )
            db.add(new_space)
        else:
            print("Co-Working Space 402 already exists, skipping...")

        # Space 2: Creative Corner
        space_exists2 = db.query(resource.CoWorkingSpace).filter_by(room_no="806").first()
        if not space_exists2: # Fixed: was checking space_exists before
            print("Seeding Creative Corner...")
            new_space2 = resource.CoWorkingSpace(
                name="Creative Corner",
                description="Inspiration zone with art supplies",
                type="coworking_space",
                room_no="806",
                capacity=8,
                min_guests=0,       # Anyone can book alone
                image_url=None
            )
            db.add(new_space2)
        else:
            print("Co-Working Space 806 already exists, skipping...")

        # 4. Seed Locker
        locker_exists = db.query(resource.Locker).filter_by(locker_no="L-101").first()
        if not locker_exists:
            print("Seeding Locker...")
            new_locker = resource.Locker(
                name="West Wing Locker",
                description="Secure storage near the entrance",
                type="locker",
                locker_no="L-101",
                size="Large",       # Added the new size field
                image_url=None
            )
            db.add(new_locker)
        else:
            print("Locker L-101 already exists, skipping...")

        # 5. Seed Equipment (New)
        equip_exists = db.query(resource.Equipment).filter_by(serial_no="SN-999-X").first()
        if not equip_exists:
            print("Seeding Equipment...")
            new_equip = resource.Equipment(
                name="Sony 4K Projector",
                description="High-resolution projector for presentations",
                type="equipment",
                serial_no="SN-999-X",
                image_url=None
            )
            db.add(new_equip)

        # 6. Seed Bookings (Updated to 2026 and using Relationship)
        # Note: Ensure user_id=2 exists in your Users table before running this
        booking_exists = db.query(booking.Booking).first()
        if not booking_exists:
            print("Seeding initial Bookings...")
            
            # Booking 1: Innovation Hub (Room)
            ts1 = booking.Timeslot(
                start_time=datetime(2026, 4, 2, 10, 0), 
                end_time=datetime(2026, 4, 2, 12, 0)
            )
            b1 = booking.Booking(
                user_id=2,
                resource_id=1,
                timeslot=ts1,
                status=booking.BookingStatus.PENDING
            )
            db.add(b1)

            # Booking 2: Locker (Multi-day)
            ts2 = booking.Timeslot(
                start_time=datetime(2026, 4, 2, 9, 0), 
                end_time=datetime(2026, 4, 5, 17, 0)
            )
            b2 = booking.Booking(
                user_id=2,
                resource_id=3, # Assuming ID 3 is the Locker
                timeslot=ts2,
                status=booking.BookingStatus.PENDING
            )
            db.add(b2)

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()