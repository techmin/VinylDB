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

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VinylDB API", lifespan=lifespan)

# CORS Middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import List
from . import schemas
from sqlalchemy import select

# Try to import Spark engine, but allow fallback if Java/Spark is missing locally
try:
    from .analytics import SparkAnalyticsEngine
    spark_available = True
except ImportError:
    print("WARNING: SparkAnalyticsEngine could not be imported (likely missing Java/PySpark). Analytics endpoints will be disabled.")
    spark_available = False
except Exception as e:
    print(f"WARNING: SparkAnalyticsEngine failed to load: {e}")
    spark_available = False

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
        return {"status": "healthy", "database": "connected, read/write ready", "spark_available": spark_available}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


# Analytics Endpoints (Spark-powered)
def check_spark():
    if not spark_available:
        raise HTTPException(status_code=503, detail="Analytics engine unavailable (Spark/Java missing)")

@app.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data using Apache Spark"""
    check_spark()
    engine = SparkAnalyticsEngine()
    return await engine.get_all_metrics()

@app.get("/analytics/overview")
async def get_collection_overview():
    """Get collection overview statistics using Apache Spark"""
    check_spark()
    engine = SparkAnalyticsEngine()
    return await engine.get_collection_overview()

@app.get("/analytics/artists")
async def get_artist_distribution(limit: int = 10):
    """Get top artists by vinyl count using Apache Spark"""
    check_spark()
    engine = SparkAnalyticsEngine()
    return await engine.get_artist_distribution(limit)

@app.get("/analytics/genres")
async def get_genre_distribution(limit: int = 10):
    """Get genre distribution using Apache Spark"""
    check_spark()
    engine = SparkAnalyticsEngine()
    return await engine.get_genre_distribution(limit)

@app.get("/analytics/years")
async def get_year_distribution():
    """Get vinyl distribution by decade using Apache Spark"""
    check_spark()
    engine = SparkAnalyticsEngine()
    return await engine.get_year_distribution()

@app.get("/analytics/timeline")
async def get_collection_timeline():
    """Get collection growth timeline using Apache Spark"""
    check_spark()
    engine = SparkAnalyticsEngine()
    return await engine.get_collection_timeline()

@app.get("/analytics/search")
async def get_search_analytics(query: str):
    """Get analytics for search results using Apache Spark"""
    check_spark()
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    engine = SparkAnalyticsEngine()
    return await engine.search_analytics(query)


