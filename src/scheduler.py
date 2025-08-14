import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database import AsyncSessionLocal
from models import User, Credit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def add_daily_credits():
    """Add 5 credits to all users daily"""
    try:
        async with AsyncSessionLocal() as db:
            # Get all users
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            logger.info(f"Adding daily credits to {len(users)} users")
            
            for user in users:
                # Check if user has credit record
                credit_result = await db.execute(
                    select(Credit).where(Credit.user_id == user.user_id)
                )
                credit = credit_result.scalar_one_or_none()
                
                if credit:
                    # Update existing credit record
                    credit.credits += 5
                else:
                    # Create new credit record
                    new_credit = Credit(user_id=user.user_id, credits=5)
                    db.add(new_credit)
            
            await db.commit()
            logger.info("Daily credits added successfully")
            
    except Exception as e:
        logger.error(f"Error adding daily credits: {e}")

async def start_scheduler():
    """Start the background scheduler and run initial job"""
    # Schedule job to run daily at midnight UTC
    scheduler.add_job(
        add_daily_credits,
        trigger=CronTrigger(hour=0, minute=0, timezone='UTC'),
        id='daily_credits',
        name='Add daily credits to all users',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started - Daily credits job scheduled for midnight UTC")
    
    # Trigger the job immediately on startup
    logger.info("Triggering daily credits job on startup...")
    await add_daily_credits()

def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")