from datetime import datetime, timedelta
import shutil
import uuid
import os
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Table, and_, func
from sqlalchemy.orm import relationship, Session, joinedload
from fastapi import HTTPException, UploadFile, status
from app.db.base import Base
import enum

class BookingStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    OVERRIDDEN = "overridden"

booking_guests = Table(
    "booking_guests",
    Base.metadata,
    Column("booking_id", Integer, ForeignKey("bookings.booking_id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.user_id"), primary_key=True)
)

# ---------------------------------------------------------
# RESOURCE ENTITIES
# ---------------------------------------------------------

class Resource(Base):
    __tablename__ = "resources"
    resource_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    bookings = relationship("Booking", back_populates="resource", cascade="all, delete")

    __mapper_args__ = {"polymorphic_identity": "resource", "polymorphic_on": type}

    @staticmethod
    def save_image(image: UploadFile) -> str:
        if not image: return None
        upload_dir = "app/static/resources"
        os.makedirs(upload_dir, exist_ok=True)
        unique_filename = f"{uuid.uuid4()}.{image.filename.split('.')[-1]}"
        file_path = os.path.join(upload_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        return f"/static/resources/{unique_filename}"

    @classmethod
    def create_resource(cls, db: Session, resource_data: dict, image: UploadFile = None):
        image_url = cls.save_image(image)
        new_resource = cls(**resource_data, image_url=image_url)
        db.add(new_resource)
        db.commit()
        db.refresh(new_resource)
        return new_resource

    def update_resource(self, db: Session, resource_in):
        self.name = resource_in.name
        self.description = resource_in.description
        db.commit()
        db.refresh(self)
        return self

    def delete_resource(self, db: Session):
        db.delete(self)
        db.commit()
        return True

    def check_availability(self, db: Session, start: datetime, end: datetime):
        return db.query(Booking).join(Timeslot).filter(
            Booking.resource_id == self.resource_id,
            Booking.status.in_([BookingStatus.APPROVED, BookingStatus.PENDING]),
            and_(Timeslot.start_time < end, Timeslot.end_time > start)
        ).all()

    def validate_booking_rules(self, duration: timedelta, start: datetime, end: datetime, total_attendees: int, user: 'User'):
        raise NotImplementedError()


class CoWorkingSpace(Resource):
    __tablename__ = "coworking_spaces"
    resource_id = Column(Integer, ForeignKey("resources.resource_id"), primary_key=True)
    room_no = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    min_guests = Column(Integer, default=0)
    
    __mapper_args__ = {"polymorphic_identity": "coworking_space"}

    def update_resource(self, db: Session, resource_in):
        super().update_resource(db, resource_in)
        self.room_no = resource_in.room_no
        self.capacity = resource_in.capacity
        db.commit()
        return self

    def validate_booking_rules(self, duration: timedelta, start: datetime, end: datetime, total_attendees: int, user: 'User'):
        if duration.total_seconds() > 14400:
            raise HTTPException(status_code=400, detail="Rooms can only be booked for max 4 hours")
        if start.date() != end.date():
            raise HTTPException(status_code=400, detail="Room bookings must start and end on the same day")
        if total_attendees > self.capacity:
            raise HTTPException(status_code=400, detail="Capacity exceeded")
        if total_attendees < self.min_guests and user.role != "teacher":
            raise HTTPException(status_code=400, detail=f"Requires at least {self.min_guests} people.")


class Locker(Resource):
    __tablename__ = "lockers"
    resource_id = Column(Integer, ForeignKey("resources.resource_id"), primary_key=True)
    locker_no = Column(String, nullable=False)
    size = Column(String)
    
    __mapper_args__ = {"polymorphic_identity": "locker"}

    def update_resource(self, db: Session, resource_in):
        super().update_resource(db, resource_in)
        self.locker_no = resource_in.locker_no
        db.commit()
        return self

    def validate_booking_rules(self, duration: timedelta, start: datetime, end: datetime, total_attendees: int, user: 'User'):
        if duration.days < 1:
            raise HTTPException(status_code=400, detail="Lockers must be booked for at least 24 hours")
        if total_attendees > 1:
            raise HTTPException(status_code=400, detail="You cannot invite guests to a locker")


class Equipment(Resource):
    __tablename__ = "equipment"
    resource_id = Column(Integer, ForeignKey("resources.resource_id"), primary_key=True)
    serial_no = Column(String, nullable=False)
    
    __mapper_args__ = {"polymorphic_identity": "equipment"}

    def update_resource(self, db: Session, resource_in):
        super().update_resource(db, resource_in)
        self.serial_no = resource_in.serial_no
        db.commit()
        return self

    def validate_booking_rules(self, duration: timedelta, start: datetime, end: datetime, total_attendees: int, user: 'User'):
        if duration.days > 3:
            raise HTTPException(status_code=400, detail="Equipment cannot be borrowed for more than 3 days")
        if total_attendees > 1:
            raise HTTPException(status_code=400, detail="You cannot invite guests to borrow equipment")

# ---------------------------------------------------------
# BOOKING ENTITIES
# ---------------------------------------------------------

class Timeslot(Base):
    __tablename__ = "timeslots"
    timeslot_id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    booking = relationship("Booking", back_populates="timeslot", uselist=False)


class Booking(Base):
    __tablename__ = "bookings"
    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.resource_id"), nullable=False)
    timeslot_id = Column(Integer, ForeignKey("timeslots.timeslot_id"), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    guests = relationship("User", secondary=booking_guests, backref="guest_bookings")
    user = relationship("User")
    resource = relationship("Resource")
    timeslot = relationship("Timeslot", back_populates="booking")

    @staticmethod
    def get_booking(db: Session, booking_id: int):
        return db.query(Booking).filter(Booking.booking_id == booking_id).first()

    def update_status(self, db: Session, new_status: BookingStatus):
        self.status = new_status
        db.commit()
        db.refresh(self)
        return self

    def cancel(self, db: Session):
        now = datetime.now()
        if self.timeslot.start_time - now < timedelta(minutes=30):
            raise HTTPException(status_code=400, detail="Cannot cancel within 30 minutes of start time.")
        if self.status not in [BookingStatus.PENDING, BookingStatus.APPROVED]:
            raise HTTPException(status_code=400, detail="Only pending or approved bookings can be cancelled.")
        self.status = BookingStatus.CANCELLED
        db.commit()
        return True

    @staticmethod
    def resolve_conflicts(db: Session, conflicts: list['Booking'], requesting_user: 'User'):
        for conflict in conflicts:
            time_until = conflict.timeslot.start_time - datetime.now()
            is_overrideable = (
                requesting_user.role == "teacher" and 
                conflict.user.role == "student" and 
                time_until > timedelta(hours=24)
            )
            if not is_overrideable:
                raise HTTPException(status_code=400, detail="Existing bookings cannot be overridden.")
        for conflict in conflicts:
            conflict.status = BookingStatus.OVERRIDDEN

# ---------------------------------------------------------
# USER ENTITIES
# ---------------------------------------------------------

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __mapper_args__ = {"polymorphic_identity": "user", "polymorphic_on": role}

    def can_book_resource(self):
        return self.role in ["student", "teacher"]

    def request_booking(self, db: Session, resource: Resource, start: datetime, end: datetime, guest_users: list['User'] = []):
        if start >= end:
            raise HTTPException(status_code=400, detail="Start time must be before end time")
        if not self.can_book_resource():
            raise HTTPException(status_code=403, detail="User role not permitted to book resources")

        duration = end - start
        resource.validate_booking_rules(duration, start, end, len(guest_users) + 1, self)

        conflicts = resource.check_availability(db, start, end)
        if conflicts:
            Booking.resolve_conflicts(db, conflicts, self)

        new_timeslot = Timeslot(start_time=start, end_time=end)
        db.add(new_timeslot)
        db.flush()

        new_booking = Booking(
            user_id=self.user_id,
            resource_id=resource.resource_id,
            timeslot_id=new_timeslot.timeslot_id,
            status=BookingStatus.PENDING,
            guests=guest_users
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return new_booking

    def cancel_booking(self, db: Session, booking: Booking):
        if booking.user_id != self.user_id and self.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
        return booking.cancel(db)

    def get_booking_history(self, db: Session):
        return db.query(Booking).options(
            joinedload(Booking.timeslot), joinedload(Booking.resource), 
            joinedload(Booking.user), joinedload(Booking.guests)
        ).filter(Booking.user_id == self.user_id).order_by(Booking.created_at.desc()).all()


class Student(User):
    __tablename__ = "students"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    student_id = Column(String, unique=True)
    __mapper_args__ = {"polymorphic_identity": "student"}

    @staticmethod
    def findUserByStudentId(db: Session, student_id: str):
        return db.query(Student).filter(Student.student_id == student_id).first()


class Teacher(User):
    __tablename__ = "teachers"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    __mapper_args__ = {"polymorphic_identity": "teacher"}


class Admin(User):
    __tablename__ = "admins"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    __mapper_args__ = {"polymorphic_identity": "admin"}

    def get_all_booking_history(self, db: Session, target_user_id: int = None):
        query = db.query(Booking).options(
            joinedload(Booking.timeslot), joinedload(Booking.resource), 
            joinedload(Booking.user), joinedload(Booking.guests)
        )
        if target_user_id:
            query = query.filter(Booking.user_id == target_user_id)
        return query.order_by(Booking.created_at.desc()).all()

    def manage_booking_status(self, db: Session, booking: Booking, new_status: BookingStatus):
        return booking.update_status(db, new_status)