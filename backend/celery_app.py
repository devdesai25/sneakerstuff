from celery import Celery
from backend.config import settings
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import os

celery_app = Celery(
    "sneakdrop",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("CELERY_BACKEND_URL", "redis://localhost:6379/1"),
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
    poolclass=NullPool,
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
    }
)

CelerySessionLocal = async_sessionmaker(
    bind=celery_engine,
    expire_on_commit=False
)
