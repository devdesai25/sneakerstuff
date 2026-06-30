from fastapi import HTTPException
from backend.celery_app import celery_app
from backend.database import AsyncSessionLocal
from backend.models.entry import Entry
from backend.models.reservations import Reservation
from backend.enums.drop_status import DropStatus
from backend.helpers.drop_helpers import get_drop_or_404
from datetime import datetime
import redis
import random

r = redis.Redis(host="localhost", port=6379, db=2)

@celery_app.task(bind=True, max_retries=3)
def activate_drop(self, drop_id: int):
    db = AsyncSessionLocal()

    try:
        drop = get_drop_or_404(drop_id, db)
        drop.status = DropStatus.ENTRY_OPEN
        db.commit()

    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=10)
    
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3)
def close_drop(self, drop_id:int):
    db = AsyncSessionLocal()

    try:
        drop = get_drop_or_404(drop_id, db)
        drop.status = DropStatus.ENTRY_CLOSED
        db.commit()

    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=10)

    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3)
def select_winners(self, drop_id: int):

    db = AsyncSessionLocal()
    try:
        entries = (
            db.query(Entry)
            .filter(Entry.drop_id == drop_id)
            .all()
        )

        if not entries:
            raise HTTPException(
                status_code=404,
                detail="Entries not found"
            )
        
        random.shuffle(entries)

        for rank, entry in enumerate(entries, start=1):
            entry.ranking = rank

        db.commit()

    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=10)
    
    finally:
        db.close()