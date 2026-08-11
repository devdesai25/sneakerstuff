import pytest_asyncio
import pytest

from httpx import AsyncClient
from httpx import ASGITransport

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.main import app
from backend.database import Base
from backend.database import get_db
import backend.models
from backend.auth.jwt import encode
from backend.tests.factories import (
    create_drop,
    create_product,
    create_user,
)
from backend.tests.test_database import (
    engine,
    TestingSessionLocal,
)

from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_celery(monkeypatch):
    monkeypatch.setattr("celery.app.task.Task.apply_async", MagicMock())

@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS drop_sizes, order_items, reservations, entries, drops, product_sizes, products, users CASCADE;"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def db():

    async with engine.connect() as connection:

        transaction = await connection.begin()

        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()

@pytest_asyncio.fixture
async def client(db):

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
) as client:
        
        yield client

        app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def product(db, user):
    return await create_product(
        db,
        created_by=user.id
    )

@pytest_asyncio.fixture
async def admin_user(db):
    return await create_user(
        db,
        username="admin",
        email="admin@123.com",
        role="admin",
    )

@pytest_asyncio.fixture
async def user(db):
    return await create_user(db)

@pytest_asyncio.fixture
async def drop(db, product):
    return await create_drop(
        db,
        product
    )

@pytest.fixture
def admin_token(admin_user):

    return encode(
        {
            "sub": str(admin_user.id)
        }
    )

@pytest.fixture
def user_token(user):

    return encode(
        {
            "sub": str(user.id)
        }
    )

@pytest.fixture
def admin_headers(admin_token):

    return {
        "Authorization": f"Bearer {admin_token}"
    }

@pytest.fixture
def user_headers(user_token):

    return {
        "Authorization": f"Bearer {user_token}"
    }