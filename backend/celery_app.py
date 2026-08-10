import uuid
from celery import Celery
from backend.config import settings
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import os
import ssl

broker_url = (
    os.environ.get("CELERY_BROKER_URL") 
    or os.environ.get("REDIS_URL") 
    or os.environ.get("REDIS_PUBLIC_URL") 
    or os.environ.get("REDIS_PRIVATE_URL") 
    or "redis://localhost:6379/0"
)

backend_url = (
    os.environ.get("CELERY_BACKEND_URL") 
    or os.environ.get("REDIS_URL") 
    or os.environ.get("REDIS_PUBLIC_URL") 
    or os.environ.get("REDIS_PRIVATE_URL") 
    or "redis://localhost:6379/1"
)

celery_app = Celery(
    "sneakdrop",
    broker=broker_url,
    backend=backend_url,
    include=["backend.tasks.drop_tasks"]
)

celery_conf = {
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "broker_connection_retry_on_startup": True,
    "broker_transport_options": {
        "max_retries": 3,
        "interval_start": 0.2,
        "interval_step": 0.2,
        "interval_max": 0.5,
    }
}

if broker_url.startswith("rediss://"):
    celery_conf["broker_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}
if backend_url.startswith("rediss://"):
    celery_conf["redis_backend_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}

celery_app.conf.update(**celery_conf)

celery_engine = create_async_engine(
    url=settings.DATABASE_URL, 
    poolclass=NullPool,
    connect_args={
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4().hex}__",
    }
)

CelerySessionLocal = async_sessionmaker(
    bind=celery_engine,
    expire_on_commit=False
)
