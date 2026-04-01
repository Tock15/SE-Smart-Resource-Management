from email import message

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi import UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import Admin, User
from app.routes.authRoute import get_current_user
from app.services.resourceService import ResourceService
from app.services.bookingService import BookingService
from app.models.booking import BookingStatus
from app.services.notificationService import NotificationService
from app.routes.bookingRoute import BookingResponse
from typing import List




class ResourceCreate(BaseModel):
    name: str
    description: str
    type: str
    room_no: str | None = None
    capacity: int | None = None
    locker_no: str | None = None
    serial_no: str | None = None



router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/resources", status_code=status.HTTP_201_CREATED)
async def create_resource(
    name: str = Form(...),
    description: str = Form(...),
    type: str = Form(...),
    room_no: str = Form(None),
    capacity: int = Form(None),
    min_guests: int = Form(None),
    locker_no: str = Form(None),
    serial_no: str = Form(None),
    image: UploadFile = File(None), # The image file
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    resource_dict = {
        "name": name, "description": description, "type": type,
        "room_no": room_no, "capacity": capacity, "min_guests": min_guests,
        "locker_no": locker_no, "serial_no": serial_no
    }
    
    return ResourceService.create_resource(db, resource_dict, image)

@router.put("/resources/{resource_id}")
async def update_resource(resource_id: int, resource_in: ResourceCreate, db: Session = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    if not current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update resources"
        )

    resource = ResourceService.update_resource(db, resource_id, resource_in)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return {"message": "Resource updated successfully", "resource_id": resource.resource_id}

@router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: int, 
    db: Session = Depends(get_db), 
    current_user: Admin = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    success = ResourceService.delete_resource(db, resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    return {"message": "Resource deleted successfully"}
# app/routes/adminRoute.py additions

@router.put("/bookings/{booking_id}/approve")
async def approve_booking(
    booking_id: int, 
    db: Session = Depends(get_db), 
    current_user: Admin = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    booking = BookingService.update_booking_status(db, booking_id, BookingStatus.APPROVED)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # TODO: Trigger Notification here
    NotificationService.send_approval_email(booking.user.email, booking.resource.name)
    return {"message": "Booking approved", "booking_id": booking_id}

@router.put("/bookings/{booking_id}/reject")
async def reject_booking(
    booking_id: int, 
    db: Session = Depends(get_db), 
    current_user: Admin = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    booking = BookingService.update_booking_status(db, booking_id, BookingStatus.REJECTED)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # TODO: Trigger Notification here
    NotificationService.send_rejection_email(booking.user.email, booking.resource.name)
    return {"message": "Booking rejected", "booking_id": booking_id}




@router.get("/users/{user_id}/bookings", response_model=List[BookingResponse])
async def get_user_booking_history(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: Admin = Depends(get_current_user)
):
    # Strict admin check
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only admins can view specific user histories"
        )
    
    
    history = BookingService.get_booking_history(db, user_id=user_id, is_admin=True)
    
    if not history:
        return []
        
    return history