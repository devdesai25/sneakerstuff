#import redis
import random
import asyncio
from fastapi import HTTPException
from sqlalchemy import select, exists
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, timedelta

from backend.celery_app import celery_app, CelerySessionLocal
from backend.models.entry import Entry
from backend.models.reservations import Reservation
from backend.models.order import Order
from backend.models.drops import Drop
from backend.models.order_items import OrderItem
from backend.enums.drop_status import DropStatus
from backend.enums.order_status import OrderStatus
from backend.helpers.drop_helpers import get_drop_or_404, get_entries_or_404

#r = redis.Redis(host="localhost", port=6379, db=2)
async def _activate_drop(self, drop_id):

    async with CelerySessionLocal() as db: 

        try:
            drop = await get_drop_or_404(drop_id, db)
            drop.status = DropStatus.ENTRY_OPEN
            await db.commit()

        except Exception as exc:
            await db.rollback()
            raise self.retry(exc=exc, countdown=10)
        
        finally:
            await db.close()

@celery_app.task(bind=True, max_retries=3)
def activate_drop(self, drop_id: int):
    return asyncio.run(_activate_drop(self, drop_id))    
async def _close_drop(self, drop_id):
    async with CelerySessionLocal() as db: 

        try:    
            drop = await get_drop_or_404(drop_id, db)
            drop.status = DropStatus.ENTRY_CLOSED
            await db.flush()

            entries = await get_entries_or_404(drop_id, db)

            if not entries:
                raise HTTPException(
                    status_code=404,
                    detail="Entries not found"
                )
            
            random.shuffle(entries)

            for rank, entry in enumerate(entries, start=1):
                entry.ranking = rank

            await db.commit()

            select_winners.apply_async(args=[drop_id], countdown=30)

        except Exception as exc:
            await db.rollback()
            raise self.retry(exc=exc, countdown=10)

        finally:
            await db.close()

@celery_app.task(bind=True, max_retries=3)
def close_drop(self, drop_id:int):
    return asyncio.run(_close_drop(self, drop_id))

async def _select_winners(self, drop_id):
    async with CelerySessionLocal() as db: 


        try:
            drop = (
                await db.execute(
                    select(Drop)
                    .where(Drop.drop_id == drop_id)
                    .with_for_update()
                )
            ).scalar_one_or_none()

            entries = await get_entries_or_404(drop_id, db)

            if not entries:
                raise HTTPException(
                    status_code=404,
                    detail="Entries not found"
                )
            
            stmt = (
                select(Entry)
                .where(Entry.drop_id == drop_id)
                .order_by(Entry.ranking.asc())
                .limit(drop.drop_inventory)
            )
            
            result = await db.execute(stmt)
            winners = result.scalars().all()
            
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

            for winner in winners:
                order = Order(
                    user_id = winner.user_id,
                    total_amount = drop.product_price,
                    status = OrderStatus.PENDING,
                    expires_at = expires_at,
                    address = winner.address
                )
                db.add(order)
                await db.flush()

                order_item = OrderItem(
                    order_id = order.order_id,
                    product_id = winner.drop.product_id,
                    quantity = 1,
                    unit_price = drop.product_price,
                    subtotal = drop.product_price,
                    size = winner.size
                )
                db.add(order_item)
                drop.drop_inventory -= 1

                reservation = Reservation(
                    entry_id = winner.entry_id,
                    order_id = order.order_id
                )
                db.add(reservation)
                await db.flush()

                expire_unpaid_reservations.apply_async(
                    args=[reservation.reservation_id], eta=order.expires_at)
                        
            drop.status == DropStatus.CLAIMING
            
            await db.commit()
            #await db.refresh(winners)
            
        except Exception as exc:
            await db.rollback()
            raise self.retry(exc=exc, countdown=10)
        
        finally:
            await db.close()

@celery_app.task(bind=True, max_retries=3)
def select_winners(self, drop_id: int):
    return asyncio.run(_select_winners(self, drop_id))

async def _expire_unpaid_reservations(self, reservation_id):
    async with CelerySessionLocal() as db: 
        try:
            # Query the reservation, preloading the order and the entry's drop details
            reservation = (
                await db.execute(
                    select(Reservation)
                    .where(Reservation.reservation_id == reservation_id)
                    .options(
                        selectinload(Reservation.order),
                        selectinload(Reservation.entry)
                    )
                )
            ).scalar_one_or_none()

            # If the reservation doesn't exist, exit gracefully
            if not reservation:
                return

            # If the order is already PAID, do not expire it
            if reservation.order and reservation.order.status == OrderStatus.PAID:
                return
            
            # Set the unpaid order status to EXPIRED
            if reservation.order:
                reservation.order.status = OrderStatus.EXPIRED

            drop = (
                await db.execute(
                    select(Drop)
                    .where(Drop.drop_id == reservation.entry.drop_id)
                    .with_for_update()
                )
            ).scalar_one_or_none()
            # Increment the drop inventory because the reservation slot is freed up
            drop.drop_inventory += 1
            await db.flush()

            # Query the next highest ranked entry that doesn't have a reservation
            stmt = (
                select(Entry)
                .where(
                    Entry.drop_id == drop.drop_id,
                    ~exists().where(Reservation.entry_id == Entry.entry_id)
                )
                .order_by(Entry.ranking.asc())
                .limit(1)
            )

            result = await db.execute(stmt)
            new_winner = result.scalar_one_or_none()

            if new_winner:
                # We have a new winner! Decrement drop inventory back by 1
                drop.drop_inventory -= 1
                
                expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

                new_order = Order(
                    user_id = new_winner.user_id,
                    total_amount = drop.product_price,
                    status = OrderStatus.PENDING,
                    expires_at = expires_at,
                    address = new_winner.address
                )
                db.add(new_order)
                await db.flush()

                new_order_item = OrderItem(
                    order_id = new_order.order_id,
                    product_id = drop.product_id,
                    quantity = 1,
                    unit_price = drop.product_price,
                    subtotal = drop.product_price,
                    size = new_winner.size
                )
                db.add(new_order_item)

                new_reservation = Reservation(
                    entry_id = new_winner.entry_id,
                    order_id = new_order.order_id
                )
                db.add(new_reservation)
                await db.flush()

                # Schedule the check for the new reservation's payment status
                expire_unpaid_reservations.apply_async(
                    args=[new_reservation.reservation_id],
                    eta=new_order.expires_at 
                )
        
            await db.commit()
            if reservation:
                await db.refresh(reservation)
        
        except Exception as exc:
            await db.rollback()
            raise self.retry(exc=exc, countdown=10)
        finally:
            await db.close()

@celery_app.task(bind=True, max_retries=3)
def expire_unpaid_reservations(self, reservation_id):   
    return asyncio.run(_expire_unpaid_reservations(self, reservation_id))