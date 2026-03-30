import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated

import jwt
from app.services.authService import AuthService
from app.models.user import Student, Teacher, User, Admin
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from datetime import timedelta

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

class UserCreate(BaseModel):
    username: str
    email: str
    student_id: str | None = None
    password: str
    role: str

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="A user with this email already exists."
        )
    hashed_password = AuthService.hash_password(user_in.password)
    if user_in.role == "student":
        new_user = Student(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            student_id=user_in.student_id  # student-specific field
        )
    elif user_in.role == "teacher":
        new_user = Teacher(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password
        )
    elif user_in.role == "admin":
        new_user = Admin(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid role provided.")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.user_id}

@router.post("/login")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not AuthService.verify_password(user.hashed_password, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = AuthService.create_access_token(user.username, user.user_id,timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: Session = Depends(get_db)):
    try:
        payload = AuthService.validate_jwt(token)
        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
        )
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
@router.get("/profile")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


    
