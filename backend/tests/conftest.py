import pytest_asyncio

from httpx import AsyncClient
from httpx import ASGITransport

from backend.main import app
from backend.database import Base
from backend.database import get_db

from tests.test_database import (
    engine,
    TestingSessionLocal,
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def override_get_db():

    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixtures
async def db():

    async with TestingSessionLocal() as session:
        yield session

        await session.rollback()

@pytest_asyncio.fixture
async def client():

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
) as client:
        
        yield client