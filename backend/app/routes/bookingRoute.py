from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.routes.authRoute import get_current_user
from app.models.user import User
from app.services.bookingService import BookingService
from pydantic import BaseModel
from datetime import datetime
from app.models.booking import BookingStatus

router = APIRouter(prefix="/bookings", tags=["bookings"])

class TimeslotResponse(BaseModel):
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime

class BookingResponse(BaseModel):
    booking_id: int
    status: BookingStatus
    resource_id: int
    user_id: int
    timeslot: TimeslotResponse



    class Config:
        from_attributes = True
        
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def request_booking(
    booking_in: BookingCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_booking = BookingService.create_booking(
        db=db,
        user_id=current_user.user_id,
        resource_id=booking_in.resource_id,
        start=booking_in.start_time,
        end=booking_in.end_time
    )
    return new_booking

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.user_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this booking")
    return booking
