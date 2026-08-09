import uuid
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.config import settings

metadata = MetaData()
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=5,
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4().hex}__",
    }
)

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