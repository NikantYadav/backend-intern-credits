from fastapi import FastAPI
from routes.credits import router as credits_router
from routes.users import router as users_router
from routes.admin import router as admin_router
from routes.schema import router as schema_router
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from contextlib import asynccontextmanager
from scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start background scheduler and trigger initial job
    await start_scheduler()
    
    yield
    
    # Cleanup on shutdown
    stop_scheduler()
    await engine.dispose()

app = FastAPI(title="Credits API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       
    allow_credentials=True,
    allow_methods=["*"],       
    allow_headers=["*"],
)

# Include routers
app.include_router(credits_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(schema_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)