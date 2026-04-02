from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.resource import CoWorkingSpace, Locker, Equipment, Resource
from app.models.user import User
from app.routes.authRoute import get_current_user
from app.routes.bookingRoute import TimeslotResponse
from datetime import datetime

class viewResource(BaseModel):
    resource_id: int
    name: str
    description: str | None = None
    type: str
    room_no: str | None = None
    capacity: int | None = None
    min_guests: int | None = None
    image_url: str | None = None
    locker_no: str | None = None
    serial_no: str | None = None
    class Config:
        from_attributes = True
class viewBookingForResource(BaseModel):
    booking_id: int
    user_id: int
    status: str
    user_role : str
    timeslot: TimeslotResponse

    class Config:
        from_attributes = True
    @classmethod
    def from_orm(cls, obj):
        data = super().model_validate(obj)
        data.user_role = obj.user.role
        return data
    
class viewIndividualResource(viewResource):
    bookings: list[viewBookingForResource] = []


router = APIRouter(
    prefix="/resources",
    tags=["resources"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[viewResource])
async def list_resources(db: Session = Depends(get_db)):
    return db.query(Resource).all()


@router.get("/coworking-spaces", response_model=list[viewResource])
async def list_coworking_spaces(db: Session = Depends(get_db)):
    return db.query(CoWorkingSpace).all()

@router.get("/lockers", response_model=list[viewResource])
async def list_lockers(db: Session = Depends(get_db)):  
    return db.query(Locker).all()    

@router.get("/equipments", response_model=list[viewResource])
async def list_equipment(db: Session = Depends(get_db)):
    return db.query(Equipment).all()


@router.get("/{resource_id}", response_model=viewIndividualResource)
async def get_resource(resource_id: int, date: str, db: Session = Depends(get_db)):
    
    # Query resource and filter by ID
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    if resource.type == "coworking_space":
        # Specifically fetch CoWorkingSpace to access its specific fields and bookings
        try:
            target_date = datetime.strptime(date, "%d-%m-%Y").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="For coworking, use DD-MM-YYYY")
        resource = db.query(CoWorkingSpace).filter(CoWorkingSpace.resource_id == resource_id).first()
        
        # Filter bookings by date and ensure user role is accessible
        bookings_on_date = []
        for b in resource.bookings:
            if b.timeslot.start_time.date() == target_date or b.timeslot.end_time.date() == target_date:
                # Attach the role directly to the booking object for the response model to pick up
                b.user_role = b.user.role 
                bookings_on_date.append(b)
        
        result = viewIndividualResource.from_orm(resource)
        result.bookings = bookings_on_date
        return result
    else:
        # Logic for Month-Year (MM-YYYY)
        try:
            # Parse to the first day of that month
            target_month = datetime.strptime(date, "%m-%Y")
        except ValueError:
            raise HTTPException(status_code=400, detail="For this resource, use MM-YYYY")

        bookings_in_month = [
            b for b in resource.bookings 
            if b.timeslot.start_time.month == target_month.month 
            and b.timeslot.start_time.year == target_month.year
        ]

        for b in bookings_in_month:
            b.user_role = b.user.role

        result = viewIndividualResource.from_attributes(resource)
        result.bookings = bookings_in_month
        return result
    