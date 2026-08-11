import uuid
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.config import settings

metadata = MetaData()
db_url = settings.DATABASE_URL
if db_url and db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

connect_args = {}
if "asyncpg" in db_url:
    connect_args = {
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4().hex}__",
    }

engine = create_async_engine(
    db_url,
    pool_size=10,
    max_overflow=5,
    connect_args=connect_args,
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