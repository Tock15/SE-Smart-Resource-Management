from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.resource import CoWorkingSpace, Locker, Equipment, Resource
from app.models.user import User
from app.routes.authRoute import get_current_user

class viewResource(BaseModel):
    resource_id: int
    name: str
    description: str | None = None
    type: str
    room_no: str | None = None
    capacity: int | None = None
    locker_no: str | None = None
    serial_no: str | None = None

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


@router.get("/{resource_id}", response_model=viewResource)
async def get_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource