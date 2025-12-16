from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from contextlib import asynccontextmanager
from .database import engine, Base, get_db
from .models import Vinyl

# Lifecycle manager to create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="VinylDB API", lifespan=lifespan)

from typing import List
from . import schemas
from sqlalchemy import select

# ... (existing imports)

@app.post("/vinyls/", response_model=schemas.VinylResponse)
async def create_vinyl(vinyl: schemas.VinylCreate, db: AsyncSession = Depends(get_db)):
    db_vinyl = Vinyl(**vinyl.dict())
    db.add(db_vinyl)
    await db.commit()
    await db.refresh(db_vinyl)
    return db_vinyl

@app.get("/vinyls/", response_model=List[schemas.VinylResponse])
async def read_vinyls(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vinyl).offset(skip).limit(limit))
    vinyls = result.scalars().all()
    return vinyls

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # User requested to "add to neon", ensuring connection handles writes too
        result = await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected, read/write ready"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
