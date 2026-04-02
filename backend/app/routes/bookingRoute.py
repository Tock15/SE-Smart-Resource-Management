from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.routes.authRoute import get_current_user
from app.models.user import User
from app.services.bookingService import BookingService
from pydantic import BaseModel
from datetime import datetime
from app.models.booking import BookingStatus
from typing import List


router = APIRouter(prefix="/bookings", tags=["bookings"])

class TimeslotResponse(BaseModel):
    timeslot_id: int
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True
class ResourceResponse(BaseModel):
    resource_id: int
    name: str
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    user_id: int
    username: str
    student_id: str

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime
    guests: List[int] = []

class BookingResponse(BaseModel):
    booking_id: int
    status: BookingStatus
    timeslot: TimeslotResponse
    resource: ResourceResponse
    user: UserResponse
    guests: List[UserResponse] = []

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
    if not current_user.can_book_resource():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not allowed to book resources")
    
    new_booking = BookingService.create_booking(
        db=db,
        user_id=current_user.user_id,
        resource_id=booking_in.resource_id,
        start=booking_in.start_time,
        end=booking_in.end_time,
        guest_ids=booking_in.guests
    )
    return new_booking


@router.get("/", response_model=List[BookingResponse])
async def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    is_admin = current_user.role == "admin"
    print(f"User {current_user.username} is admin: {is_admin}")

    history = BookingService.get_booking_history(
        db=db, 
        user_id=current_user.user_id if not is_admin else None, 
        is_admin=is_admin
    )
    return history


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

@router.get("/existing/{student_id}", response_model=UserResponse)
async def get_existing_user(student_id: str, db: Session = Depends(get_db)):
    res = BookingService.findUserByStudentId(db, student_id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return res


