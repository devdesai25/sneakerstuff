import os
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

engine = create_async_engine(
    DATABASE_URL, 
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False,
)