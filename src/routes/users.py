from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from database import get_db
from models import User

router = APIRouter(prefix="/users", tags=["users"])

# Pydantic models for request/response
class UserCreate(BaseModel):
    email: str
    name: str

class UserResponse(BaseModel):
    user_id: int
    email: str
    name: str
    
    class Config:
        from_attributes = True

@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user"""
    
    # Check if user with email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Create new user
    new_user = User(
        email=user_data.email,
        name=user_data.name
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get user by ID"""
    
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user