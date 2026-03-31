
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.resource import Resource, CoWorkingSpace, Locker, Equipment
from fastapi import HTTPException, status

class ResourceService:
    @staticmethod
    def create_resource(db: Session, resource_in):
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resource type"
            )
        
        
        db.add(new_resource)
        db.commit()
        db.refresh(new_resource)
        return new_resource

    @staticmethod
    def delete_resource(db: Session, resource_id: int):
        resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
        if not resource:
            return False
        db.delete(resource)
        db.commit()
        return True
    @staticmethod
    def update_resource(db: Session, resource_id: int, resource_in):
        resource = db.query(Resource).filter(Resource.resource_id == resource_id).first()
        if not resource:
            return None
        
        if isinstance(resource, CoWorkingSpace):
            resource.name = resource_in.name
            resource.description = resource_in.description
            resource.room_no = resource_in.room_no
            resource.capacity = resource_in.capacity
        elif isinstance(resource, Locker):
            resource.name = resource_in.name
            resource.description = resource_in.description
            resource.locker_no = resource_in.locker_no
        elif isinstance(resource, Equipment):
            resource.name = resource_in.name
            resource.description = resource_in.description
            resource.serial_no = resource_in.serial_no

        db.commit()
        db.refresh(resource)
        return resource
    
    
    