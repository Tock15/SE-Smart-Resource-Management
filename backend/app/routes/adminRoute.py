from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.resource import CoWorkingSpace, Locker, Equipment
from app.models.user import Admin
from app.routes.authRoute import get_current_user


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
async def create_resource(resource_in: ResourceCreate, db: Session = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    if not current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create resources"
        )
    
    if resource_in.type == "coworking_space":
        new_resource = CoWorkingSpace(
            name=resource_in.name,
            description=resource_in.description,
            room_no=resource_in.room_no,
            capacity=resource_in.capacity
        )
    elif resource_in.type == "locker":
        new_resource = Locker(
            name=resource_in.name,
            description=resource_in.description,
            locker_no=resource_in.locker_no
        )
    elif resource_in.type == "equipment":
        new_resource = Equipment(
            name=resource_in.name,
            description=resource_in.description,
            serial_no=resource_in.serial_no
        )
    else:
        raise HTTPException(
            status_code=400, 
            detail="Invalid resource type. Must be 'coworking_space', 'locker', or 'equipment'."
        )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return {"message": "Resource created successfully", "resource_id": new_resource.resource_id}


