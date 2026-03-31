from email import message

from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.resource import CoWorkingSpace, Locker, Equipment, Resource
from app.models.user import Admin
from app.routes.authRoute import get_current_user
from app.services.resourceService import ResourceService


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
    
    return ResourceService.create_resource(db, resource_in)

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
