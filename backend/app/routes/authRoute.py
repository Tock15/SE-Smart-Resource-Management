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
    new_user = AuthService.register_user(db, user_in)
    
    return {
        "message": "User registered successfully", 
        "user_id": new_user.user_id
    }

@router.post("/login")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    return AuthService.authenticate_user(db, form_data.username, form_data.password)

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


    
