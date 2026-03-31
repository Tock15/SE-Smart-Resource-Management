
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.booking import Booking, Timeslot, BookingStatus
from fastapi import HTTPException, status


class BookingService:
    @staticmethod
    def check_availability(db: Session, resource_id: int, start: datetime, end: datetime):
        query = db.query(Booking).join(Timeslot).filter(
            Booking.resource_id == resource_id,
            Booking.status.in_([BookingStatus.APPROVED, BookingStatus.PENDING]),
            and_(
                Timeslot.start_time < end,
                Timeslot.end_time > start
            )
        )
        return query.first() is None

    @staticmethod
    def create_booking(db: Session, user_id: int, resource_id: int, start: datetime, end: datetime):
        if start >= end:
            raise HTTPException(status_code=400, detail="Start time must be before end time")
        
        if not BookingService.check_availability(db, resource_id, start, end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Resource is already booked for this time period"
            )

        new_timeslot = Timeslot(start_time=start, end_time=end)
        db.add(new_timeslot)
        db.flush() 

        new_booking = Booking(
            user_id=user_id,
            resource_id=resource_id,
            timeslot_id=new_timeslot.timeslot_id,
            status=BookingStatus.PENDING
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return new_booking
    
    @staticmethod
    def get_booking(db: Session, booking_id: int):
        return db.query(Booking).filter(Booking.booking_id == booking_id).first()

    @staticmethod
    def get_booking_history(db: Session, user_id: int = None, is_admin: bool = False):
        query = db.query(Booking)
        if not is_admin:
            query = query.filter(Booking.user_id == user_id)
        return query.order_by(Booking.created_at.desc()).all()