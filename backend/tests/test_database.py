import os
import uuid
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

# Load environment variables from root or backend .env
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL")
)

# Ensure database URL uses async driver (postgresql+asyncpg://)
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

connect_args = {}
if "asyncpg" in DATABASE_URL:
    connect_args = {
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4().hex}__",
    }

engine = create_async_engine(
    DATABASE_URL, 
    poolclass=NullPool,
    connect_args=connect_args,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False,
)