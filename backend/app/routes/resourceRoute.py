from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.resource import Resource
from app.models.user import User
from app.routes.authRoute import get_current_user

class viewResource(BaseModel):
    resource_id: int
    name: str
    description: str
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

@router.get("/{resource_id}", response_model=viewResource)
async def get_resource(resource_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
   
    resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return resource