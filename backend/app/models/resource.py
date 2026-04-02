from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.sql import func

class Resource(Base):
    __tablename__ = "resources"
    resource_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    bookings = relationship("Booking", back_populates="resource")

    __mapper_args__ = {
        "polymorphic_identity": "resource",
        "polymorphic_on": type,
    }

class CoWorkingSpace(Resource):
    __tablename__ = "coworking_spaces"
    resource_id = Column(Integer, ForeignKey("resources.resource_id"), primary_key=True)
    room_no = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    min_guests = Column(Integer, default=0)
    

    __mapper_args__ = {
        "polymorphic_identity": "coworking_space",
    }

class Locker(Resource):
    __tablename__ = "lockers"
    resource_id = Column(Integer, ForeignKey("resources.resource_id"), primary_key=True)
    locker_no = Column(String, nullable=False)
    size = Column(String)


    __mapper_args__ = {
        "polymorphic_identity": "locker",
    }

class Equipment(Resource):
    __tablename__ = "equipment"
    resource_id = Column(Integer, ForeignKey("resources.resource_id"), primary_key=True)
    serial_no = Column(String, nullable=False)
    __mapper_args__ = {
        "polymorphic_identity": "equipment",
    }

