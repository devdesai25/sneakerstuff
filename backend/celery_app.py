from celery import Celery

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