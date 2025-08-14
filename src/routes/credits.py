from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from database import get_db
from models import User, Credit

router = APIRouter(prefix="/api/credits", tags=["credits"])

# Pydantic models
class AmountRequest(BaseModel):
    amount: int

class CreditResponse(BaseModel):
    user_id: int
    credits: int
    last_updated: str
    
    class Config:
        from_attributes = True

@router.get("/{user_id}")
async def get_credits(user_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve current credit balance and last update timestamp"""
    
    # Check if user exists
    user_result = await db.execute(select(User).where(User.user_id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's credits
    credit_result = await db.execute(select(Credit).where(Credit.user_id == user_id))
    credit = credit_result.scalar_one_or_none()
    
    if not credit:
        # Create initial credit record if doesn't exist
        credit = Credit(user_id=user_id, credits=0)
        db.add(credit)
        await db.commit()
        await db.refresh(credit)
    
    return {
        "user_id": credit.user_id,
        "credits": credit.credits,
        "last_updated": credit.last_updated.isoformat()
    }

@router.post("/{user_id}/add")
async def add_credits(user_id: int, request: AmountRequest, db: AsyncSession = Depends(get_db)):
    """Add credits to user account"""
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # Check if user exists
    user_result = await db.execute(select(User).where(User.user_id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create credit record
    credit_result = await db.execute(select(Credit).where(Credit.user_id == user_id))
    credit = credit_result.scalar_one_or_none()
    
    if not credit:
        credit = Credit(user_id=user_id, credits=request.amount)
        db.add(credit)
    else:
        credit.credits += request.amount
    
    await db.commit()
    await db.refresh(credit)
    
    return {
        "message": f"Added {request.amount} credits",
        "user_id": credit.user_id,
        "new_balance": credit.credits,
        "last_updated": credit.last_updated.isoformat()
    }

@router.post("/{user_id}/deduct")
async def deduct_credits(user_id: int, request: AmountRequest, db: AsyncSession = Depends(get_db)):
    """Subtract credits from user account (no negative balances)"""
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # Check if user exists
    user_result = await db.execute(select(User).where(User.user_id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get credit record
    credit_result = await db.execute(select(Credit).where(Credit.user_id == user_id))
    credit = credit_result.scalar_one_or_none()
    
    if not credit:
        raise HTTPException(status_code=400, detail="User has no credit record")
    
    # Check if sufficient balance
    if credit.credits < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient credits")
    
    credit.credits -= request.amount
    await db.commit()
    await db.refresh(credit)
    
    return {
        "message": f"Deducted {request.amount} credits",
        "user_id": credit.user_id,
        "new_balance": credit.credits,
        "last_updated": credit.last_updated.isoformat()
    }

@router.patch("/{user_id}/reset")
async def reset_credits(user_id: int, db: AsyncSession = Depends(get_db)):
    """Reset user's credits to zero"""
    
    # Check if user exists
    user_result = await db.execute(select(User).where(User.user_id == user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create credit record
    credit_result = await db.execute(select(Credit).where(Credit.user_id == user_id))
    credit = credit_result.scalar_one_or_none()
    
    if not credit:
        credit = Credit(user_id=user_id, credits=0)
        db.add(credit)
    else:
        credit.credits = 0
    
    await db.commit()
    await db.refresh(credit)
    
    return {
        "message": "Credits reset to zero",
        "user_id": credit.user_id,
        "credits": credit.credits,
        "last_updated": credit.last_updated.isoformat()
    }