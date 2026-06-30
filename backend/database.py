from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.config import settings

metadata = MetaData()
engine  = create_async_engine(settings.DATABASE_URL, pool_size=20, max_overflow=0)

class Base(DeclarativeBase):
    pass
    
AsyncSessionLocal = async_sessionmaker(bind = engine, autocommit=False, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

"""
def get_db():
    
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        
"""