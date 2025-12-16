import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

from pathlib import Path

# Load .env from the same directory as this file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL set for the application")

import ssl

# Handle SSL for asyncpg
connect_args = {}
if "sslmode=require" in DATABASE_URL:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx
    connect_args["statement_cache_size"] = 0
    DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "")
    DATABASE_URL = DATABASE_URL.replace("&sslmode=require", "")

# Create Async Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Log SQL for debugging (disable in production)
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create Async Session Local
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
