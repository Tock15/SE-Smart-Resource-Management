
from datetime import datetime
import shutil
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.resource import Resource, CoWorkingSpace, Locker, Equipment
from fastapi import HTTPException, status, UploadFile, File, Form
import uuid
import os


class ResourceService:
    @staticmethod
    def save_image(image: UploadFile) -> str:
        if not image:
            return None

        upload_dir = "app/static/resources"
        os.makedirs(upload_dir, exist_ok=True)
       
        file_extension = image.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        return f"/static/resources/{unique_filename}"
    @staticmethod
    def create_resource(db: Session, resource_data: dict, image: UploadFile = None):
        image_url = ResourceService.save_image(image)
        res_type = resource_data.get("type")

        if res_type == "coworking_space":
            new_resource = CoWorkingSpace(
                name=resource_data["name"],
                description=resource_data["description"],
                room_no=resource_data["room_no"],
                capacity=resource_data["capacity"],
                image_url=image_url
            )
        elif res_type == "locker":
            new_resource = Locker(
                name=resource_data["name"],
                description=resource_data["description"],
                locker_no=resource_data["locker_no"],
                image_url=image_url
            )
        elif res_type == "equipment":
            new_resource = Equipment(
                name=resource_data["name"],
                description=resource_data["description"],
                serial_no=resource_data["serial_no"],
                image_url=image_url
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

    
    

