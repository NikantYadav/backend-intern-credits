from fastapi import APIRouter

router = APIRouter(prefix="/credits", tags=["credits"])

@router.get("/")
async def get_credits():
    return {
        "credits": 1000,
        "user_id": "user123",
        "last_updated": "2025-01-14"
    }

@router.post("/add")
async def add_credits(amount: int):
    return {
        "message": f"Added {amount} credits",
        "new_balance": 1000 + amount
    }

@router.get("/balance")
async def get_balance():
    return {"balance": 1000}