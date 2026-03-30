from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.base import Base
from sqlalchemy.sql import func
from passlib.context import CryptContext




pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": role,
    }

class Student(User):
    __tablename__ = "students"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    student_id = Column(String, unique=True) # Specific to students

    __mapper_args__ = {
        "polymorphic_identity": "student",
    }

class Teacher(User):
    __tablename__ = "teachers"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "teacher",
    }

class Admin(User):
    __tablename__ = "admins"
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }