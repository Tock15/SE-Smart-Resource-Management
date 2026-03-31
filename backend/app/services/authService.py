from sqlalchemy import or_

import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from dotenv import load_dotenv
import os
import bcrypt
from app.models.user import Student, Teacher, Admin, User
from sqlalchemy.orm import Session


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


class AuthService:
    @staticmethod
    def create_access_token(username: str, user_id: str, role: str, expires_delta: timedelta):
        encode = {'sub': username, 'id': user_id, 'role': role}
        expires = datetime.now(timezone.utc) + expires_delta
        encode.update({"exp": expires})
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def validate_jwt(token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def hash_password(plain_password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(hashed_password, plain_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def register_user(db: Session, user_in):
        existing_user = db.query(User).filter(or_(User.email == user_in.email, User.username == user_in.username)).first()

        if existing_user:
            if existing_user.email == user_in.email:
                raise HTTPException(status_code=400, detail="Email already registered.")
            if existing_user.username == user_in.username:
                raise HTTPException(status_code=400, detail="Username already taken.")
        hashed_password = AuthService.hash_password(user_in.password)

        user_data = {
            "username": user_in.username,
            "email": user_in.email,
            "hashed_password": hashed_password
        }

        if user_in.role == "student":
            new_user = Student(**user_data, student_id=user_in.student_id)
        elif user_in.role == "teacher":
            new_user = Teacher(**user_data)
        elif user_in.role == "admin":
            new_user = Admin(**user_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid role provided.")
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


    @staticmethod
    def authenticate_user(db: Session, username, password):
        user = db.query(User).filter(User.username == username).first()

        if not user or not AuthService.verify_password(user.hashed_password, password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = AuthService.create_access_token(
            user.username, 
            user.user_id, 
            user.role,
            timedelta(minutes=60)
        )
        return {"access_token": token, "token_type": "bearer"}