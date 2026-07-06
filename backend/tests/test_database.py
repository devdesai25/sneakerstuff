from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool


DATABASE_URL=(
    "postgresql+asyncpg://postgres:63ZjZQfVXnfhUAyQ@db.qbqlymjwmjublnsgjpbq.supabase.co:5432/postgres"
)

engine = create_async_engine(
    DATABASE_URL, 
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False,
)