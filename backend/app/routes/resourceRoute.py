from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated
from pydantic import BaseModel, model_validator
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
    timeslot: TimeslotResponse
    user_role: str | None = None 

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def get_user_role(cls, data):
        # If it's an ORM object, extract the role from the user relationship
        if hasattr(data, 'user') and data.user:
            data.user_role = data.user.role
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
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Standardize result object
    result = viewIndividualResource.model_validate(resource)
    filtered_bookings = []

    try:
        if resource.type == "coworking_space":
            target_date = datetime.strptime(date, "%d-%m-%Y").date()
            # Use a list comprehension to avoid manual attribute injection
            filtered_bookings = [
                b for b in resource.bookings 
                if b.timeslot.start_time.date() == target_date
            ]
        else:
            target_month = datetime.strptime(date, "%m-%Y")
            filtered_bookings = [
                b for b in resource.bookings 
                if b.timeslot.start_time.month == target_month.month 
                and b.timeslot.start_time.year == target_month.year
            ]
    except ValueError:
        detail = "Use DD-MM-YYYY for coworking" if resource.type == "coworking_space" else "Use MM-YYYY"
        raise HTTPException(status_code=400, detail=detail)

    result.bookings = filtered_bookings
    return result