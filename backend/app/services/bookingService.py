
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from app.models.booking import Booking, Timeslot, BookingStatus
from app.models.resource import Resource
from app.models.user import User
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
    def create_booking(db: Session, user_id: int, resource_id: int, start: datetime, end: datetime, guest_ids: list[int] = []):
        if start >= end:
            raise HTTPException(status_code=400, detail="Start time must be before end time")
        resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")

        duration = end - start

        if resource.type == "coworking_space":
            # Rule: Max 4 hours, must be same day
            if duration.total_seconds() > 14400: # 4 hours
                raise HTTPException(status_code=400, detail="Rooms can only be booked for max 4 hours")
            if start.date() != end.date():
                raise HTTPException(status_code=400, detail="Room bookings must start and end on the same day")
            
            # Check Capacity for Guests
            total_attendees = len(guest_ids) + 1
            if total_attendees > resource.capacity:
                raise HTTPException(status_code=400, detail="Capacity exceeded")
            if total_attendees < resource.min_guests:
                raise HTTPException(
                    status_code=400, 
                    detail=f"This room requires at least {resource.min_guests} people. Please invite more guests."
                )

        elif resource.type == "locker":
            # Rule: Minimum 1 day, No guests allowed
            if duration.days < 1:
                raise HTTPException(status_code=400, detail="Lockers must be booked for at least 24 hours")
            if guest_ids:
                raise HTTPException(status_code=400, detail="You cannot invite guests to a locker")

        elif resource.type == "equipment":
            # Rule: Max 3 days
            if duration.days > 3:
                raise HTTPException(status_code=400, detail="Equipment cannot be borrowed for more than 3 days")
            if guest_ids:
                raise HTTPException(status_code=400, detail="You cannot invite guests to borrow equipment")
        
  
        
        
        if not BookingService.check_availability(db, resource_id, start, end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Resource is already booked for this time period"
            )

        new_timeslot = Timeslot(start_time=start, end_time=end)
        db.add(new_timeslot)
        db.flush() 
        guest_users = []
        if guest_ids:
            guest_users = db.query(User).filter(User.user_id.in_(guest_ids)).all()

        new_booking = Booking(
            user_id=user_id,
            resource_id=resource_id,
            timeslot_id=new_timeslot.timeslot_id,
            status=BookingStatus.PENDING,
            guests = guest_users
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
        query = db.query(Booking).options(joinedload(Booking.timeslot), 
                                           joinedload(Booking.resource), 
                                           joinedload(Booking.user),
                                           joinedload(Booking.guests)) 
        
        if not is_admin:
            query = query.filter(Booking.user_id == user_id)
        else:
            if user_id:
                query = query.filter(Booking.user_id == user_id)
                
        return query.order_by(Booking.created_at.desc()).all()
    @staticmethod
    def update_booking_status(db: Session, booking_id: int, status: BookingStatus):
        booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
        if not booking:
            return None
        
        booking.status = status
        db.commit()
        db.refresh(booking)
        return booking