from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class BookingStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class Timeslot(Base):
    __tablename__ = "timeslots"

    timeslot_id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Relationship to Booking
    booking = relationship("Booking", back_populates="timeslot", uselist=False)

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.resource_id"), nullable=False)
    timeslot_id = Column(Integer, ForeignKey("timeslots.timeslot_id"), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User")
    resource = relationship("Resource")
    timeslot = relationship("Timeslot", back_populates="booking")