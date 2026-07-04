from celery import Celery
from backend.config import settings
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

celery_app = Celery(
    "sneakdrop",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=["backend.tasks.drop_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True
)

celery_engine = create_async_engine(
    url=settings.DATABASE_URL, 
    poolclass=NullPool
)

CelerySessionLocal = async_sessionmaker(
    bind=celery_engine,
    expire_on_commit=False
)
